// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * @title TriangleDiceEscrow
 * @notice 1:1 betting escrow for Triangle Dice game
 * @dev Game logic is off-chain; only money handling is on-chain
 *
 * Flow:
 * 1. Player A: createMatch(stakeAmount, timeoutSec) -> matchId
 * 2. Player B: joinMatch(matchId)
 * 3. Player A: startMatch(matchId) -> game begins
 * 4. During game: ping(matchId) to reset timeout
 * 5. End: submitResult(result, sigA, sigB) OR claimTimeoutWin(matchId)
 */
contract TriangleDiceEscrow {
    using ECDSA for bytes32;

    // ============ Constants ============
    uint256 public constant FEE_BPS = 20; // 0.2%
    uint256 public constant FEE_CAP = 20000; // 0.02 USDC (6 decimals)
    uint256 public constant MIN_STAKE = 500000; // 0.5 USDC
    uint256 public constant MAX_STAKE = 10000000; // 10 USDC
    uint256 public constant MIN_TIMEOUT = 60;
    uint256 public constant MAX_TIMEOUT = 120;

    // ============ EIP-712 ============
    bytes32 public constant DOMAIN_TYPEHASH = keccak256(
        "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
    );
    bytes32 public constant RESULT_TYPEHASH = keccak256(
        "Result(uint256 matchId,uint8 finalScoreA,uint8 finalScoreB,uint8 tiebreakerRoll,address winner,uint256 nonce)"
    );
    bytes32 public immutable DOMAIN_SEPARATOR;

    // ============ Types ============
    enum MatchStatus {
        None,
        Created,
        Joined,
        Started,
        Settled,
        Cancelled,
        TimeoutClaimed
    }

    struct Match {
        address playerA;
        address playerB;
        uint256 stakeAmount;
        uint256 timeoutSec;
        uint256 lastActivity;
        MatchStatus status;
        uint256 nonce; // for replay protection
    }

    struct Result {
        uint256 matchId;
        uint8 finalScoreA;
        uint8 finalScoreB;
        uint8 tiebreakerRoll;
        address winner;
        uint256 nonce;
    }

    // ============ State ============
    IERC20 public immutable usdc;
    address public feeCollector;
    uint256 public matchCounter;
    mapping(uint256 => Match) public matches;
    uint256 public collectedFees;

    // ============ Events ============
    event MatchCreated(uint256 indexed matchId, address indexed playerA, uint256 stakeAmount, uint256 timeoutSec);
    event MatchJoined(uint256 indexed matchId, address indexed playerB);
    event MatchStarted(uint256 indexed matchId, uint256 startTime);
    event MatchSettled(uint256 indexed matchId, address indexed winner, uint256 payout, uint256 fee);
    event MatchCancelled(uint256 indexed matchId);
    event TimeoutClaimed(uint256 indexed matchId, address indexed winner);
    event Pinged(uint256 indexed matchId, address indexed player);

    // ============ Errors ============
    error InvalidStakeAmount();
    error InvalidTimeout();
    error MatchNotFound();
    error NotPlayerA();
    error NotPlayer();
    error AlreadyJoined();
    error NotJoined();
    error NotStarted();
    error AlreadySettled();
    error TimeoutNotReached();
    error InvalidSignature();
    error InvalidWinner();
    error NonceMismatch();
    error TransferFailed();

    // ============ Constructor ============
    constructor(address _usdc, address _feeCollector) {
        usdc = IERC20(_usdc);
        feeCollector = _feeCollector;

        DOMAIN_SEPARATOR = keccak256(
            abi.encode(
                DOMAIN_TYPEHASH,
                keccak256("TriangleDiceEscrow"),
                keccak256("1"),
                block.chainid,
                address(this)
            )
        );
    }

    // ============ Match Lifecycle ============

    /**
     * @notice Create a new match
     * @param stakeAmount Amount each player stakes (0.5-10 USDC)
     * @param timeoutSec Timeout in seconds (60-120)
     * @return matchId The ID of the created match
     */
    function createMatch(uint256 stakeAmount, uint256 timeoutSec) external returns (uint256 matchId) {
        if (stakeAmount < MIN_STAKE || stakeAmount > MAX_STAKE) revert InvalidStakeAmount();
        if (timeoutSec < MIN_TIMEOUT || timeoutSec > MAX_TIMEOUT) revert InvalidTimeout();

        matchId = ++matchCounter;

        matches[matchId] = Match({
            playerA: msg.sender,
            playerB: address(0),
            stakeAmount: stakeAmount,
            timeoutSec: timeoutSec,
            lastActivity: block.timestamp,
            status: MatchStatus.Created,
            nonce: 0
        });

        // Transfer stake from player A
        if (!usdc.transferFrom(msg.sender, address(this), stakeAmount)) revert TransferFailed();

        emit MatchCreated(matchId, msg.sender, stakeAmount, timeoutSec);
    }

    /**
     * @notice Join an existing match
     * @param matchId The match to join
     */
    function joinMatch(uint256 matchId) external {
        Match storage m = matches[matchId];
        if (m.status != MatchStatus.Created) revert MatchNotFound();
        if (m.playerB != address(0)) revert AlreadyJoined();
        if (msg.sender == m.playerA) revert AlreadyJoined();

        m.playerB = msg.sender;
        m.status = MatchStatus.Joined;
        m.lastActivity = block.timestamp;

        // Transfer stake from player B
        if (!usdc.transferFrom(msg.sender, address(this), m.stakeAmount)) revert TransferFailed();

        emit MatchJoined(matchId, msg.sender);
    }

    /**
     * @notice Start the match (only player A can start)
     * @param matchId The match to start
     */
    function startMatch(uint256 matchId) external {
        Match storage m = matches[matchId];
        if (m.status != MatchStatus.Joined) revert NotJoined();
        if (msg.sender != m.playerA) revert NotPlayerA();

        m.status = MatchStatus.Started;
        m.lastActivity = block.timestamp;

        emit MatchStarted(matchId, block.timestamp);
    }

    /**
     * @notice Reset the timeout timer (call during game to prevent timeout)
     * @param matchId The match to ping
     */
    function ping(uint256 matchId) external {
        Match storage m = matches[matchId];
        if (m.status != MatchStatus.Started) revert NotStarted();
        if (msg.sender != m.playerA && msg.sender != m.playerB) revert NotPlayer();

        m.lastActivity = block.timestamp;

        emit Pinged(matchId, msg.sender);
    }

    /**
     * @notice Claim win by timeout
     * @param matchId The match where opponent timed out
     */
    function claimTimeoutWin(uint256 matchId) external {
        Match storage m = matches[matchId];
        if (m.status != MatchStatus.Started) revert NotStarted();
        if (msg.sender != m.playerA && msg.sender != m.playerB) revert NotPlayer();
        if (block.timestamp < m.lastActivity + m.timeoutSec) revert TimeoutNotReached();

        m.status = MatchStatus.TimeoutClaimed;

        // Winner is whoever called this (opponent timed out)
        uint256 totalPot = m.stakeAmount * 2;
        uint256 fee = _calculateFee(totalPot);
        uint256 payout = totalPot - fee;

        collectedFees += fee;

        if (!usdc.transfer(msg.sender, payout)) revert TransferFailed();

        emit TimeoutClaimed(matchId, msg.sender);
    }

    /**
     * @notice Cancel match if no one joined yet
     * @param matchId The match to cancel
     */
    function cancelIfNotJoined(uint256 matchId) external {
        Match storage m = matches[matchId];
        if (m.status != MatchStatus.Created) revert AlreadyJoined();
        if (msg.sender != m.playerA) revert NotPlayerA();

        m.status = MatchStatus.Cancelled;

        // Refund player A
        if (!usdc.transfer(m.playerA, m.stakeAmount)) revert TransferFailed();

        emit MatchCancelled(matchId);
    }

    /**
     * @notice Submit final result with both players' signatures
     * @param result The game result
     * @param sigA Player A's signature
     * @param sigB Player B's signature
     */
    function submitResult(
        Result calldata result,
        bytes calldata sigA,
        bytes calldata sigB
    ) external {
        Match storage m = matches[result.matchId];
        if (m.status != MatchStatus.Started) revert NotStarted();
        if (result.nonce != m.nonce) revert NonceMismatch();
        if (result.winner != m.playerA && result.winner != m.playerB) revert InvalidWinner();

        // Verify signatures
        bytes32 structHash = keccak256(
            abi.encode(
                RESULT_TYPEHASH,
                result.matchId,
                result.finalScoreA,
                result.finalScoreB,
                result.tiebreakerRoll,
                result.winner,
                result.nonce
            )
        );
        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );

        address signerA = digest.recover(sigA);
        address signerB = digest.recover(sigB);

        if (signerA != m.playerA || signerB != m.playerB) revert InvalidSignature();

        // Mark as settled
        m.status = MatchStatus.Settled;
        m.nonce++;

        // Calculate payout
        uint256 totalPot = m.stakeAmount * 2;
        uint256 fee = _calculateFee(totalPot);
        uint256 payout = totalPot - fee;

        collectedFees += fee;

        // Pay winner
        if (!usdc.transfer(result.winner, payout)) revert TransferFailed();

        emit MatchSettled(result.matchId, result.winner, payout, fee);
    }

    // ============ View Functions ============

    function getMatch(uint256 matchId) external view returns (Match memory) {
        return matches[matchId];
    }

    function getTimeRemaining(uint256 matchId) external view returns (uint256) {
        Match storage m = matches[matchId];
        if (m.status != MatchStatus.Started) return 0;

        uint256 deadline = m.lastActivity + m.timeoutSec;
        if (block.timestamp >= deadline) return 0;
        return deadline - block.timestamp;
    }

    // ============ Admin Functions ============

    function withdrawFees() external {
        uint256 amount = collectedFees;
        collectedFees = 0;
        if (!usdc.transfer(feeCollector, amount)) revert TransferFailed();
    }

    function setFeeCollector(address _feeCollector) external {
        require(msg.sender == feeCollector, "Not fee collector");
        feeCollector = _feeCollector;
    }

    // ============ Internal Functions ============

    function _calculateFee(uint256 amount) internal pure returns (uint256) {
        uint256 fee = (amount * FEE_BPS) / 10000;
        return fee > FEE_CAP ? FEE_CAP : fee;
    }

    // ============ EIP-712 Helpers ============

    function hashResult(Result calldata result) external view returns (bytes32) {
        bytes32 structHash = keccak256(
            abi.encode(
                RESULT_TYPEHASH,
                result.matchId,
                result.finalScoreA,
                result.finalScoreB,
                result.tiebreakerRoll,
                result.winner,
                result.nonce
            )
        );
        return keccak256(
            abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash)
        );
    }
}
