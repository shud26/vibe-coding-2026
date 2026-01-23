import { useState } from 'react';
import { createDiceRoll, getDiceWinner } from '../lib/dice';

interface DiceRollerProps {
  onRollComplete: (roll: number) => void;
  disabled?: boolean;
  label?: string;
}

export function DiceRoller({ onRollComplete, disabled, label = 'Roll Dice' }: DiceRollerProps) {
  const [rolling, setRolling] = useState(false);
  const [result, setResult] = useState<number | null>(null);

  const handleRoll = () => {
    setRolling(true);

    // Animate dice roll
    let count = 0;
    const interval = setInterval(() => {
      setResult(Math.floor(Math.random() * 6) + 1);
      count++;

      if (count >= 10) {
        clearInterval(interval);
        const { roll } = createDiceRoll();
        setResult(roll);
        setRolling(false);
        onRollComplete(roll);
      }
    }, 100);
  };

  return (
    <div className="dice-roller">
      <button
        onClick={handleRoll}
        disabled={disabled || rolling}
        className="btn-dice"
      >
        {rolling ? 'Rolling...' : label}
      </button>
      {result !== null && (
        <div className="dice-result">
          <span className="dice-face">{getDiceFace(result)}</span>
          <span className="dice-value">{result}</span>
        </div>
      )}
    </div>
  );
}

// Dice commit-reveal for 2 players
interface CommitRevealDiceProps {
  myCommitment: string | null;
  opponentCommitment: string | null;
  myRoll: number | null;
  opponentRoll: number | null;
  onCommit: (commitment: string, roll: number, salt: string) => void;
  onReveal: () => void;
  isMyTurn: boolean;
  phase: 'commit' | 'reveal' | 'done';
}

export function CommitRevealDice({
  myCommitment,
  opponentCommitment,
  myRoll,
  opponentRoll,
  onCommit,
  onReveal,
  isMyTurn,
  phase,
}: CommitRevealDiceProps) {
  const [localRoll, setLocalRoll] = useState<{ roll: number; salt: string; commitment: string } | null>(null);

  const handleCommit = () => {
    const { roll, salt, commitment } = createDiceRoll();
    setLocalRoll({ roll, salt, commitment });
    onCommit(commitment, roll, salt);
  };

  const handleReveal = () => {
    onReveal();
  };

  return (
    <div className="commit-reveal-dice">
      {phase === 'commit' && (
        <div className="commit-phase">
          <p>Both players need to commit their dice rolls</p>
          {!myCommitment && isMyTurn && (
            <button onClick={handleCommit} className="btn-dice">
              Roll & Commit
            </button>
          )}
          {myCommitment && <p className="status">Your commitment: {myCommitment.slice(0, 10)}...</p>}
          {opponentCommitment && <p className="status">Opponent committed</p>}
          {!opponentCommitment && myCommitment && <p className="waiting">Waiting for opponent...</p>}
        </div>
      )}

      {phase === 'reveal' && (
        <div className="reveal-phase">
          <p>Both committed! Time to reveal</p>
          {localRoll && !myRoll && (
            <button onClick={handleReveal} className="btn-dice">
              Reveal ({localRoll.roll})
            </button>
          )}
          {myRoll && <p className="status">Your roll: {myRoll}</p>}
          {opponentRoll && <p className="status">Opponent roll: {opponentRoll}</p>}
        </div>
      )}

      {phase === 'done' && myRoll && opponentRoll && (
        <div className="done-phase">
          <div className="dice-results">
            <div className="dice-result">
              <span className="player">You</span>
              <span className="dice-face">{getDiceFace(myRoll)}</span>
              <span className="dice-value">{myRoll}</span>
            </div>
            <div className="vs">VS</div>
            <div className="dice-result">
              <span className="player">Opponent</span>
              <span className="dice-face">{getDiceFace(opponentRoll)}</span>
              <span className="dice-value">{opponentRoll}</span>
            </div>
          </div>
          <p className="winner">
            {getDiceWinner(myRoll, opponentRoll) === 'tie'
              ? 'Tie! Roll again'
              : getDiceWinner(myRoll, opponentRoll) === 'A'
              ? 'You win!'
              : 'Opponent wins!'}
          </p>
        </div>
      )}
    </div>
  );
}

// Unicode dice faces
function getDiceFace(value: number): string {
  const faces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
  return faces[value - 1] || '?';
}
