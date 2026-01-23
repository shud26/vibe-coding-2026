import { useState, useEffect } from 'react';
import { useAccount, useSwitchChain, useChainId } from 'wagmi';
import { WalletConnect } from '../components/WalletConnect';
import {
  useUSDCBalance,
  useUSDCAllowance,
  useApproveUSDC,
  useCreateMatch,
  useJoinMatch,
  useStartMatch,
  useMatch,
  useMintUSDC,
  MatchStatus,
} from '../hooks/useEscrow';
import { GAME_CONFIG, toUSDCUnits, fromUSDCUnits, CONTRACTS, CHAIN_ID } from '../config';

interface LobbyProps {
  onMatchCreated?: (matchId: bigint) => void;
  onMatchJoined?: (matchId: bigint) => void;
  onGameStart?: (matchId: bigint, playerA: `0x${string}`, playerB: `0x${string}`) => void;
}

export function Lobby({ onMatchCreated: _onMatchCreated, onMatchJoined: _onMatchJoined, onGameStart }: LobbyProps) {
  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { switchChain } = useSwitchChain();

  // Form states
  const [stakeAmount, setStakeAmount] = useState('1');
  const [joinMatchId, setJoinMatchId] = useState('');
  const [createdMatchId, setCreatedMatchId] = useState<string | null>(null);
  const [checkMatchId, setCheckMatchId] = useState(''); // For checking existing matches
  const [txStatus, setTxStatus] = useState<string>('');

  const isWrongNetwork = chainId !== CHAIN_ID;

  // Read hooks
  const { data: balance, refetch: refetchBalance } = useUSDCBalance(address);
  const { data: allowance, refetch: refetchAllowance } = useUSDCAllowance(address);

  // Write hooks
  const { approve, isPending: approving, isSuccess: approveSuccess, error: approveError } = useApproveUSDC();
  const { createMatch, isPending: creating, isSuccess: createSuccess, receipt: createReceipt, error: createError } = useCreateMatch();
  const { joinMatch, isPending: joining, isSuccess: joinSuccess, error: joinError } = useJoinMatch();
  const { startMatch, isPending: starting, isSuccess: startSuccess, error: startError } = useStartMatch();
  const { mint, isPending: minting, isSuccess: mintSuccess } = useMintUSDC();

  // Match tracking for host (from creation OR from check input)
  const hostMatchIdStr = createdMatchId || checkMatchId;
  const hostMatchId = hostMatchIdStr ? (() => { try { return BigInt(hostMatchIdStr); } catch { return null; } })() : null;
  const { data: hostMatchData, refetch: refetchHostMatch } = useMatch(hostMatchId);
  const hostMatch = hostMatchData as { playerA: string; playerB: string; stakeAmount: bigint; status: number } | undefined;

  // Match preview for guest
  const guestMatchId = joinMatchId ? (() => { try { return BigInt(joinMatchId); } catch { return null; } })() : null;
  const { data: guestMatchData, refetch: refetchGuestMatch } = useMatch(guestMatchId);
  const guestMatch = guestMatchData as { playerA: string; playerB: string; stakeAmount: bigint; status: number } | undefined;

  // Parse matchId from createMatch receipt
  useEffect(() => {
    if (createSuccess && createReceipt && !createdMatchId) {
      // Find the MatchCreated event from the Escrow contract (not USDC Transfer!)
      const escrowAddress = CONTRACTS.ESCROW.toLowerCase();
      const matchCreatedLog = createReceipt.logs.find(log =>
        log.address.toLowerCase() === escrowAddress &&
        log.topics && log.topics.length >= 2
      );
      if (matchCreatedLog && matchCreatedLog.topics[1]) {
        const matchId = BigInt(matchCreatedLog.topics[1]).toString();
        console.log('Parsed Match ID:', matchId);
        setCreatedMatchId(matchId);
        setTxStatus(`Match #${matchId} created!`);
      }
    }
  }, [createSuccess, createReceipt, createdMatchId]);

  // Refetch on success
  useEffect(() => {
    if (approveSuccess) {
      refetchAllowance();
      setTxStatus('USDC approved!');
    }
  }, [approveSuccess, refetchAllowance]);

  useEffect(() => {
    if (mintSuccess) {
      refetchBalance();
      setTxStatus('100 Test USDC minted!');
    }
  }, [mintSuccess, refetchBalance]);

  useEffect(() => {
    if (joinSuccess) {
      refetchGuestMatch();
      setTxStatus(`Joined match #${joinMatchId}!`);
    }
  }, [joinSuccess, refetchGuestMatch, joinMatchId]);

  useEffect(() => {
    if (startSuccess) {
      refetchHostMatch();
      setTxStatus('Game started!');
    }
  }, [startSuccess, refetchHostMatch]);

  // Transition to game board when match starts
  useEffect(() => {
    if (hostMatch?.status === MatchStatus.Started && hostMatchId && onGameStart) {
      console.log('Game started! Transitioning to board...');
      onGameStart(
        hostMatchId,
        hostMatch.playerA as `0x${string}`,
        hostMatch.playerB as `0x${string}`
      );
    }
  }, [hostMatch?.status, hostMatchId, hostMatch?.playerA, hostMatch?.playerB, onGameStart]);

  // Also check for guest match status
  useEffect(() => {
    if (guestMatch?.status === MatchStatus.Started && guestMatchId && onGameStart) {
      console.log('Game started! Transitioning to board (guest)...');
      onGameStart(
        guestMatchId,
        guestMatch.playerA as `0x${string}`,
        guestMatch.playerB as `0x${string}`
      );
    }
  }, [guestMatch?.status, guestMatchId, guestMatch?.playerA, guestMatch?.playerB, onGameStart]);

  // Calculate values
  const stakeInUnits = toUSDCUnits(parseFloat(stakeAmount) || 0);
  const currentAllowance = (allowance as bigint) || 0n;
  const currentBalance = (balance as bigint) || 0n;
  const guestStakeRequired = guestMatch?.stakeAmount || 0n;
  const needsApprovalForCreate = currentAllowance < stakeInUnits;
  const needsApprovalForJoin = guestMatch ? currentAllowance < guestStakeRequired : false;

  // Handlers
  const handleMint = () => {
    if (address) {
      setTxStatus('Minting USDC...');
      mint(address, toUSDCUnits(100));
    }
  };

  const handleApprove = (amount: bigint) => {
    setTxStatus('Approving USDC...');
    approve(amount);
  };

  const handleCreateMatch = () => {
    setTxStatus('Creating match...');
    createMatch(stakeInUnits, BigInt(GAME_CONFIG.ONCHAIN_TIMEOUT));
  };

  const handleJoinMatch = () => {
    console.log('=== HANDLE JOIN MATCH ===');
    console.log('guestMatchId:', guestMatchId?.toString());
    console.log('address:', address);

    if (!guestMatchId) {
      setTxStatus('Enter a valid Match ID');
      return;
    }

    setTxStatus('Opening wallet... Please confirm transaction');
    joinMatch(guestMatchId);
  };

  const handleStartMatch = () => {
    if (hostMatchId) {
      setTxStatus('Starting game...');
      startMatch(hostMatchId);
    }
  };

  // Get any error message
  const getErrorMessage = () => {
    const error = approveError || createError || joinError || startError;
    if (error) {
      return (error as Error).message || 'Transaction failed';
    }
    return null;
  };

  return (
    <div className="lobby">
      <header className="lobby-header">
        <h1>Triangle Dice</h1>
        <p>1v1 betting game on Base</p>
        <WalletConnect />
      </header>

      {isConnected && address ? (
        <div className="lobby-content">
          {/* Wrong Network Warning */}
          {isWrongNetwork && (
            <div className="card" style={{ background: '#ff4444', color: 'white', textAlign: 'center' }}>
              <h3>Wrong Network!</h3>
              <p>Switch to Base Sepolia (Chain ID: {CHAIN_ID})</p>
              <button
                onClick={() => switchChain({ chainId: CHAIN_ID })}
                className="btn-primary"
                style={{ marginTop: '10px' }}
              >
                Switch Network
              </button>
            </div>
          )}

          {/* Status Message */}
          {(txStatus || getErrorMessage()) && (
            <div className="card" style={{
              background: getErrorMessage() ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)',
              border: `1px solid ${getErrorMessage() ? '#ef4444' : '#10b981'}`,
              textAlign: 'center',
              padding: '12px'
            }}>
              <p style={{ color: getErrorMessage() ? '#ef4444' : '#10b981', margin: 0 }}>
                {getErrorMessage() || txStatus}
              </p>
            </div>
          )}

          {/* Balance Card */}
          <div className="card">
            <h3>Your Wallet</h3>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#a78bfa' }}>
              {fromUSDCUnits(currentBalance).toFixed(2)} USDC
            </p>
            <p style={{ fontSize: '12px', color: '#888', marginBottom: '12px' }}>
              Approved: {fromUSDCUnits(currentAllowance).toFixed(2)} USDC
            </p>
            <button
              onClick={handleMint}
              disabled={minting}
              className="btn-secondary"
              style={{ width: '100%' }}
            >
              {minting ? 'Minting...' : 'Get 100 Test USDC'}
            </button>
          </div>

          {/* ==================== HOST SECTION ==================== */}
          <div className="card">
            <h3>HOST - Create or Manage Match</h3>

            {/* Check existing match */}
            <div style={{ marginBottom: '16px', padding: '12px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '8px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Check Your Match</label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  value={checkMatchId}
                  onChange={(e) => setCheckMatchId(e.target.value)}
                  placeholder="Enter your Match ID"
                  style={{ flex: 1 }}
                />
                <button onClick={() => refetchHostMatch()} className="btn-secondary">
                  Check
                </button>
              </div>

              {/* Show match info if found */}
              {checkMatchId && hostMatch && (
                <div style={{ marginTop: '12px' }}>
                  <p style={{ fontSize: '13px', color: '#888' }}>
                    Host: {hostMatch.playerA.slice(0,6)}...{hostMatch.playerA.slice(-4)}
                    {hostMatch.playerA.toLowerCase() === address?.toLowerCase() && ' (YOU)'}
                  </p>
                  <p style={{ fontSize: '13px', color: '#888' }}>
                    Guest: {hostMatch.playerB === '0x0000000000000000000000000000000000000000' ? 'Waiting...' :
                           `${hostMatch.playerB.slice(0,6)}...${hostMatch.playerB.slice(-4)}`}
                  </p>
                  <p style={{ fontWeight: 'bold', color:
                    hostMatch.status === MatchStatus.Created ? '#fbbf24' :
                    hostMatch.status === MatchStatus.Joined ? '#10b981' :
                    hostMatch.status === MatchStatus.Started ? '#a78bfa' : '#888'
                  }}>
                    Status: {hostMatch.status === MatchStatus.Created ? 'Waiting for guest...' :
                             hostMatch.status === MatchStatus.Joined ? 'Guest joined! Ready to start!' :
                             hostMatch.status === MatchStatus.Started ? 'Game in progress!' :
                             `Status: ${hostMatch.status}`}
                  </p>

                  {/* START button if joined and you're the host */}
                  {hostMatch.status === MatchStatus.Joined && hostMatch.playerA.toLowerCase() === address?.toLowerCase() && (
                    <button
                      onClick={handleStartMatch}
                      disabled={starting}
                      className="btn-primary"
                      style={{ width: '100%', marginTop: '12px' }}
                    >
                      {starting ? 'Starting...' : 'START GAME!'}
                    </button>
                  )}
                </div>
              )}
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.1)', margin: '16px 0' }} />

            <h4 style={{ marginBottom: '12px' }}>Create New Match</h4>

            <div className="input-group">
              <label>Stake Amount (USDC)</label>
              <input
                type="number"
                value={stakeAmount}
                onChange={(e) => setStakeAmount(e.target.value)}
                min={GAME_CONFIG.MIN_STAKE}
                max={GAME_CONFIG.MAX_STAKE}
                step="0.5"
              />
              <span style={{ fontSize: '12px', color: '#888' }}>
                Range: {GAME_CONFIG.MIN_STAKE} - {GAME_CONFIG.MAX_STAKE} USDC
              </span>
            </div>

            {/* Approve for Create */}
            {needsApprovalForCreate && (
              <button
                onClick={() => handleApprove(toUSDCUnits(100))}
                disabled={approving}
                className="btn-secondary"
                style={{ width: '100%', marginBottom: '8px' }}
              >
                {approving ? 'Approving...' : `Step 1: Approve USDC`}
              </button>
            )}

            {/* Create Match */}
            <button
              onClick={handleCreateMatch}
              disabled={creating || needsApprovalForCreate || currentBalance < stakeInUnits}
              className="btn-primary"
              style={{ width: '100%' }}
            >
              {creating ? 'Creating...' :
               needsApprovalForCreate ? 'Approve USDC First' :
               currentBalance < stakeInUnits ? 'Insufficient Balance' :
               `Create Match (${stakeAmount} USDC)`}
            </button>

            {/* Created Match Info */}
            {createdMatchId && (
              <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(139, 92, 246, 0.1)', borderRadius: '8px' }}>
                <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>Match Created!</p>
                <p style={{ fontSize: '24px', fontFamily: 'monospace', color: '#a78bfa' }}>
                  ID: {createdMatchId}
                </p>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(createdMatchId);
                    setTxStatus('Match ID copied!');
                  }}
                  className="btn-secondary"
                  style={{ marginTop: '8px' }}
                >
                  Copy Match ID
                </button>

                <div style={{ marginTop: '16px' }}>
                  <button onClick={() => refetchHostMatch()} className="btn-secondary" style={{ marginRight: '8px' }}>
                    Refresh Status
                  </button>
                  <span style={{ color: '#888' }}>
                    Status: {hostMatch?.status === MatchStatus.Created ? 'Waiting for guest...' :
                             hostMatch?.status === MatchStatus.Joined ? 'Guest joined!' :
                             hostMatch?.status === MatchStatus.Started ? 'Game started!' :
                             'Loading...'}
                  </span>
                </div>

                {hostMatch?.status === MatchStatus.Joined && (
                  <button
                    onClick={handleStartMatch}
                    disabled={starting}
                    className="btn-primary"
                    style={{ width: '100%', marginTop: '12px' }}
                  >
                    {starting ? 'Starting...' : 'START GAME!'}
                  </button>
                )}

                {hostMatch?.status === MatchStatus.Started && (
                  <p style={{ color: '#10b981', marginTop: '12px', fontWeight: 'bold' }}>
                    Game in progress! (Board coming soon)
                  </p>
                )}
              </div>
            )}
          </div>

          {/* ==================== GUEST SECTION ==================== */}
          <div className="card">
            <h3>GUEST - Join Match</h3>

            <div className="input-group">
              <label>Match ID</label>
              <input
                type="text"
                value={joinMatchId}
                onChange={(e) => setJoinMatchId(e.target.value)}
                placeholder="Enter Match ID from host"
              />
            </div>

            {/* Match Preview */}
            {guestMatch && (
              <div style={{
                padding: '16px',
                background: guestMatch.playerA.toLowerCase() === address?.toLowerCase()
                  ? 'rgba(239, 68, 68, 0.2)'
                  : guestMatch.status === MatchStatus.Created ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                borderRadius: '8px',
                marginBottom: '12px',
                border: `1px solid ${guestMatch.playerA.toLowerCase() === address?.toLowerCase() ? '#ef4444' : guestMatch.status === MatchStatus.Created ? '#10b981' : '#ef4444'}`
              }}>
                <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>Match #{joinMatchId}</p>

                {/* Warning if trying to join own match */}
                {guestMatch.playerA.toLowerCase() === address?.toLowerCase() && (
                  <p style={{ color: '#ef4444', fontWeight: 'bold', marginBottom: '8px', fontSize: '14px' }}>
                    This is YOUR match! You cannot join your own match. Switch to a different wallet.
                  </p>
                )}

                <p style={{ fontSize: '13px', color: '#888', marginBottom: '4px' }}>
                  Host: {guestMatch.playerA.slice(0,6)}...{guestMatch.playerA.slice(-4)}
                </p>
                <p style={{ fontSize: '20px', color: '#a78bfa', marginBottom: '4px' }}>
                  Stake Required: <strong>{fromUSDCUnits(guestStakeRequired)} USDC</strong>
                </p>
                <p style={{
                  color: guestMatch.status === MatchStatus.Created ? '#10b981' : '#ef4444',
                  fontWeight: 'bold'
                }}>
                  {guestMatch.status === MatchStatus.Created ? 'OPEN - Ready to join!' :
                   guestMatch.status === MatchStatus.Joined ? 'Already has 2 players' :
                   guestMatch.status === MatchStatus.Started ? 'Game in progress' :
                   'Not available'}
                </p>
                {currentBalance < guestStakeRequired && guestMatch.playerA.toLowerCase() !== address?.toLowerCase() && (
                  <p style={{ color: '#f59e0b', fontSize: '13px', marginTop: '8px' }}>
                    You need {fromUSDCUnits(guestStakeRequired - currentBalance)} more USDC
                  </p>
                )}
              </div>
            )}

            {joinMatchId && !guestMatch && guestMatchId && (
              <div style={{ padding: '12px', background: 'rgba(251, 191, 36, 0.1)', borderRadius: '8px', marginBottom: '12px' }}>
                <p style={{ color: '#fbbf24' }}>Loading match info...</p>
              </div>
            )}

            {/* Approve for Join */}
            {guestMatch && guestMatch.status === MatchStatus.Created && needsApprovalForJoin && (
              <button
                onClick={() => handleApprove(guestStakeRequired > toUSDCUnits(100) ? guestStakeRequired : toUSDCUnits(100))}
                disabled={approving}
                className="btn-secondary"
                style={{ width: '100%', marginBottom: '8px' }}
              >
                {approving ? 'Approving...' : `Step 1: Approve ${fromUSDCUnits(guestStakeRequired)} USDC`}
              </button>
            )}

            {/* Join Match */}
            <button
              onClick={handleJoinMatch}
              disabled={joining || !joinMatchId || (guestMatch?.playerA.toLowerCase() === address?.toLowerCase())}
              className="btn-primary"
              style={{ width: '100%' }}
            >
              {joining ? 'Joining...' :
               !joinMatchId ? 'Enter Match ID' :
               guestMatch?.playerA.toLowerCase() === address?.toLowerCase() ? 'Cannot Join Own Match!' :
               guestMatch ? `JOIN MATCH (${fromUSDCUnits(guestStakeRequired)} USDC)` :
               'JOIN MATCH'}
            </button>

            {/* Join Success */}
            {joinSuccess && (
              <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px' }}>
                <p style={{ color: '#10b981', fontWeight: 'bold' }}>Joined Match #{joinMatchId}!</p>
                <p style={{ color: '#888', marginTop: '8px' }}>Waiting for host to start the game...</p>
                <button onClick={() => refetchGuestMatch()} className="btn-secondary" style={{ marginTop: '8px' }}>
                  Refresh Status
                </button>
                {guestMatch?.status === MatchStatus.Started && (
                  <p style={{ color: '#10b981', marginTop: '12px', fontWeight: 'bold' }}>
                    Game started! (Board coming soon)
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Debug Info */}
          <div className="card" style={{ fontSize: '11px', opacity: 0.6 }}>
            <p>Debug: USDC {CONTRACTS.USDC.slice(0,10)}... | Escrow {CONTRACTS.ESCROW.slice(0,10)}...</p>
            <p>Balance: {currentBalance.toString()} | Allowance: {currentAllowance.toString()}</p>
            <p>Guest Match: {guestMatch ? `status=${guestMatch.status}, stake=${guestMatch.stakeAmount.toString()}` : 'none'}</p>
          </div>
        </div>
      ) : (
        <div className="connect-prompt">
          <p>Connect your wallet to play</p>
        </div>
      )}
    </div>
  );
}
