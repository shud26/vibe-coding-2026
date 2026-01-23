// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {MockUSDC} from "../src/MockUSDC.sol";
import {TriangleDiceEscrow} from "../src/TriangleDiceEscrow.sol";

contract TriangleDiceEscrowTest is Test {
    MockUSDC usdc;
    TriangleDiceEscrow escrow;

    address playerA = address(0x1);
    address playerB = address(0x2);
    address feeCollector = address(0x3);

    uint256 playerAKey = 0xA11CE;
    uint256 playerBKey = 0xB0B;

    uint256 constant STAKE = 1_000_000; // 1 USDC
    uint256 constant TIMEOUT = 90; // 90 seconds

    function setUp() public {
        // Deploy contracts
        usdc = new MockUSDC();
        escrow = new TriangleDiceEscrow(address(usdc), feeCollector);

        // Setup players with proper keys
        playerA = vm.addr(playerAKey);
        playerB = vm.addr(playerBKey);

        // Mint USDC to players
        usdc.mint(playerA, 100_000_000); // 100 USDC
        usdc.mint(playerB, 100_000_000); // 100 USDC

        // Approve escrow
        vm.prank(playerA);
        usdc.approve(address(escrow), type(uint256).max);

        vm.prank(playerB);
        usdc.approve(address(escrow), type(uint256).max);
    }

    function test_CreateMatch() public {
        vm.prank(playerA);
        uint256 matchId = escrow.createMatch(STAKE, TIMEOUT);

        assertEq(matchId, 1);

        TriangleDiceEscrow.Match memory m = escrow.getMatch(matchId);
        assertEq(m.playerA, playerA);
        assertEq(m.playerB, address(0));
        assertEq(m.stakeAmount, STAKE);
        assertEq(uint8(m.status), uint8(TriangleDiceEscrow.MatchStatus.Created));
    }

    function test_JoinMatch() public {
        vm.prank(playerA);
        uint256 matchId = escrow.createMatch(STAKE, TIMEOUT);

        vm.prank(playerB);
        escrow.joinMatch(matchId);

        TriangleDiceEscrow.Match memory m = escrow.getMatch(matchId);
        assertEq(m.playerB, playerB);
        assertEq(uint8(m.status), uint8(TriangleDiceEscrow.MatchStatus.Joined));
    }

    function test_StartMatch() public {
        vm.prank(playerA);
        uint256 matchId = escrow.createMatch(STAKE, TIMEOUT);

        vm.prank(playerB);
        escrow.joinMatch(matchId);

        vm.prank(playerA);
        escrow.startMatch(matchId);

        TriangleDiceEscrow.Match memory m = escrow.getMatch(matchId);
        assertEq(uint8(m.status), uint8(TriangleDiceEscrow.MatchStatus.Started));
    }

    function test_CancelMatch() public {
        uint256 balanceBefore = usdc.balanceOf(playerA);

        vm.prank(playerA);
        uint256 matchId = escrow.createMatch(STAKE, TIMEOUT);

        uint256 balanceAfterCreate = usdc.balanceOf(playerA);
        assertEq(balanceBefore - balanceAfterCreate, STAKE);

        vm.prank(playerA);
        escrow.cancelIfNotJoined(matchId);

        uint256 balanceAfterCancel = usdc.balanceOf(playerA);
        assertEq(balanceAfterCancel, balanceBefore);
    }

    function test_TimeoutWin() public {
        vm.prank(playerA);
        uint256 matchId = escrow.createMatch(STAKE, TIMEOUT);

        vm.prank(playerB);
        escrow.joinMatch(matchId);

        vm.prank(playerA);
        escrow.startMatch(matchId);

        // Fast forward past timeout
        vm.warp(block.timestamp + TIMEOUT + 1);

        uint256 balanceBefore = usdc.balanceOf(playerA);

        vm.prank(playerA);
        escrow.claimTimeoutWin(matchId);

        uint256 balanceAfter = usdc.balanceOf(playerA);
        // Should receive 2 USDC minus fee
        uint256 totalPot = STAKE * 2;
        uint256 fee = (totalPot * 20) / 10000; // 0.2%
        assertEq(balanceAfter - balanceBefore, totalPot - fee);
    }

    function test_SubmitResult() public {
        vm.prank(playerA);
        uint256 matchId = escrow.createMatch(STAKE, TIMEOUT);

        vm.prank(playerB);
        escrow.joinMatch(matchId);

        vm.prank(playerA);
        escrow.startMatch(matchId);

        // Create result
        TriangleDiceEscrow.Result memory result = TriangleDiceEscrow.Result({
            matchId: matchId,
            finalScoreA: 5,
            finalScoreB: 3,
            tiebreakerRoll: 0,
            winner: playerA,
            nonce: 0
        });

        // Get digest
        bytes32 digest = escrow.hashResult(result);

        // Sign with both players
        (uint8 vA, bytes32 rA, bytes32 sA) = vm.sign(playerAKey, digest);
        (uint8 vB, bytes32 rB, bytes32 sB) = vm.sign(playerBKey, digest);

        bytes memory sigA = abi.encodePacked(rA, sA, vA);
        bytes memory sigB = abi.encodePacked(rB, sB, vB);

        uint256 balanceBefore = usdc.balanceOf(playerA);

        escrow.submitResult(result, sigA, sigB);

        uint256 balanceAfter = usdc.balanceOf(playerA);
        uint256 totalPot = STAKE * 2;
        uint256 fee = (totalPot * 20) / 10000;
        assertEq(balanceAfter - balanceBefore, totalPot - fee);

        TriangleDiceEscrow.Match memory m = escrow.getMatch(matchId);
        assertEq(uint8(m.status), uint8(TriangleDiceEscrow.MatchStatus.Settled));
    }

    function test_RevertInvalidStake() public {
        vm.prank(playerA);
        vm.expectRevert(TriangleDiceEscrow.InvalidStakeAmount.selector);
        escrow.createMatch(100, TIMEOUT); // Too low
    }

    function test_RevertInvalidTimeout() public {
        vm.prank(playerA);
        vm.expectRevert(TriangleDiceEscrow.InvalidTimeout.selector);
        escrow.createMatch(STAKE, 30); // Too low
    }

    function test_FeeCalculation() public {
        // For 2 USDC pot, fee = 2_000_000 * 20 / 10000 = 4000 (0.004 USDC)
        // For 20 USDC pot, fee = 20_000_000 * 20 / 10000 = 40000 > 20000, so capped at 20000

        vm.prank(playerA);
        uint256 matchId = escrow.createMatch(10_000_000, TIMEOUT); // 10 USDC stake

        vm.prank(playerB);
        escrow.joinMatch(matchId);

        vm.prank(playerA);
        escrow.startMatch(matchId);

        vm.warp(block.timestamp + TIMEOUT + 1);

        uint256 balanceBefore = usdc.balanceOf(playerA);

        vm.prank(playerA);
        escrow.claimTimeoutWin(matchId);

        uint256 balanceAfter = usdc.balanceOf(playerA);
        // 20 USDC pot - 0.02 USDC fee (capped) = 19.98 USDC = 19_980_000
        assertEq(balanceAfter - balanceBefore, 19_980_000);
    }
}
