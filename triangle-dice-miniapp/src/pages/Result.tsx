import { useState } from 'react';
import { useAccount, useSignTypedData } from 'wagmi';
import { useSubmitResult, useMatch } from '../hooks/useEscrow';
import type { GameState } from '../lib/gameEngine';
import { createTypedData } from '../lib/eip712';
import type { GameResult } from '../lib/eip712';
import { fromUSDCUnits, CONTRACTS } from '../config';

interface ResultProps {
  matchId: bigint;
  gameState: GameState;
  onBackToLobby: () => void;
}

export function Result({ matchId, gameState, onBackToLobby }: ResultProps) {
  const { address } = useAccount();
  const { signTypedDataAsync } = useSignTypedData();

  const { data: matchData } = useMatch(matchId);
  const { submitResult, isPending: submitting, isSuccess: submitted, error } = useSubmitResult();

  const [mySignature, setMySignature] = useState<`0x${string}` | null>(null);
  const [opponentSignature, setOpponentSignature] = useState<`0x${string}` | null>(null);

  const isPlayerA = address?.toLowerCase() === gameState.playerA.toLowerCase();
  const myRole = isPlayerA ? 'A' : 'B';
  const isWinner = gameState.winner === myRole;

  const match = matchData as { stakeAmount: bigint; nonce: bigint } | undefined;
  const totalPot = match ? fromUSDCUnits(match.stakeAmount * 2n) : 0;
  const fee = Math.min(totalPot * 0.002, 0.02);
  const payout = totalPot - fee;

  // Create result object for signing
  const result: GameResult = {
    matchId,
    finalScoreA: gameState.scoreA,
    finalScoreB: gameState.scoreB,
    tiebreakerRoll: 0, // No tiebreaker in new game - winner determined by score
    winner: (gameState.winner === 'A' ? gameState.playerA :
             gameState.winner === 'B' ? gameState.playerB :
             '0x0000000000000000000000000000000000000000') as `0x${string}`,
    nonce: match?.nonce ?? 0n,
  };

  const handleSign = async () => {
    try {
      const typedData = createTypedData(result, CONTRACTS.ESCROW as `0x${string}`);
      const signature = await signTypedDataAsync({
        domain: typedData.domain,
        types: typedData.types,
        primaryType: typedData.primaryType,
        message: typedData.message,
      });
      setMySignature(signature);
    } catch (e) {
      console.error('Signing failed:', e);
    }
  };

  const handleSubmit = () => {
    if (!mySignature || !opponentSignature) return;

    const sigA = isPlayerA ? mySignature : opponentSignature;
    const sigB = isPlayerA ? opponentSignature : mySignature;

    submitResult(result, sigA, sigB);
  };

  // For MVP, we'll simulate receiving opponent signature
  // In real implementation, this would come via P2P or a relay server
  const handlePasteOpponentSig = (sig: string) => {
    if (sig.startsWith('0x') && sig.length === 132) {
      setOpponentSignature(sig as `0x${string}`);
    }
  };

  return (
    <div className="result-page">
      <header className="result-header">
        <h1>{isWinner ? '🎉 You Won!' : '😔 You Lost'}</h1>
        <p className="match-id">Match #{matchId.toString()}</p>
      </header>

      {/* Final Scores */}
      <div className="final-scores">
        <div className={`score-card ${isPlayerA ? 'me' : 'opponent'}`}>
          <span className="label">{isPlayerA ? 'You' : 'Opponent'}</span>
          <span className="score">{gameState.scoreA}</span>
          <span className="role">Player A</span>
        </div>
        <div className="vs">VS</div>
        <div className={`score-card ${!isPlayerA ? 'me' : 'opponent'}`}>
          <span className="label">{!isPlayerA ? 'You' : 'Opponent'}</span>
          <span className="score">{gameState.scoreB}</span>
          <span className="role">Player B</span>
        </div>
      </div>

      {/* Draw Info */}
      {gameState.winner === 'draw' && (
        <div className="tiebreaker-info">
          <h3>Game Ended in Draw!</h3>
          <p>Both players scored {gameState.scoreA} triangles</p>
        </div>
      )}

      {/* Payout Info */}
      <div className="payout-info card">
        <h3>Settlement</h3>
        <div className="payout-row">
          <span>Total Pot</span>
          <span>{totalPot.toFixed(2)} USDC</span>
        </div>
        <div className="payout-row fee">
          <span>Fee (0.2%)</span>
          <span>-{fee.toFixed(4)} USDC</span>
        </div>
        <div className="payout-row total">
          <span>Winner Receives</span>
          <span>{payout.toFixed(2)} USDC</span>
        </div>
      </div>

      {/* Signing Section */}
      {!submitted && (
        <div className="signing-section card">
          <h3>Sign to Settle</h3>
          <p>Both players must sign the result to settle on-chain</p>

          {/* My Signature */}
          <div className="signature-box">
            <h4>Your Signature</h4>
            {!mySignature ? (
              <button onClick={handleSign} className="btn-primary">
                Sign Result
              </button>
            ) : (
              <div className="signature-display">
                <span className="check">✓</span>
                <span className="sig">{mySignature.slice(0, 20)}...</span>
                <button
                  onClick={() => navigator.clipboard.writeText(mySignature)}
                  className="btn-copy"
                >
                  Copy
                </button>
              </div>
            )}
          </div>

          {/* Opponent Signature */}
          <div className="signature-box">
            <h4>Opponent Signature</h4>
            {!opponentSignature ? (
              <div className="paste-sig">
                <input
                  type="text"
                  placeholder="Paste opponent signature (0x...)"
                  onChange={(e) => handlePasteOpponentSig(e.target.value)}
                />
                <p className="hint">
                  Share your signature with your opponent and paste theirs here
                </p>
              </div>
            ) : (
              <div className="signature-display">
                <span className="check">✓</span>
                <span className="sig">{opponentSignature.slice(0, 20)}...</span>
              </div>
            )}
          </div>

          {/* Submit Button */}
          {mySignature && opponentSignature && (
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="btn-primary btn-submit"
            >
              {submitting ? 'Submitting...' : 'Submit to Blockchain'}
            </button>
          )}

          {error && (
            <p className="error">
              Error: {(error as Error).message || 'Transaction failed'}
            </p>
          )}
        </div>
      )}

      {/* Success */}
      {submitted && (
        <div className="success-section card">
          <h3>✓ Settlement Complete</h3>
          <p>The game has been settled on-chain!</p>
          <p className="winner-info">
            {isWinner ? `You received ${payout.toFixed(2)} USDC` : 'Better luck next time!'}
          </p>
        </div>
      )}

      {/* Back to Lobby */}
      <button onClick={onBackToLobby} className="btn-secondary btn-back">
        Back to Lobby
      </button>

      {/* Game Stats */}
      <div className="game-stats-summary">
        <h3>Game Summary</h3>
        <div className="stats-grid">
          <div className="stat">
            <span className="label">Total Points</span>
            <span className="value">{gameState.points.length}</span>
          </div>
          <div className="stat">
            <span className="label">Total Lines</span>
            <span className="value">{gameState.lines.length}</span>
          </div>
          <div className="stat">
            <span className="label">Total Triangles</span>
            <span className="value">{gameState.triangles.length}</span>
          </div>
          <div className="stat">
            <span className="label">Turns Played</span>
            <span className="value">{gameState.turnNumber}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
