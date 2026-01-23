import { useState, useCallback } from 'react';
import { useAccount } from 'wagmi';
import { Canvas } from '../components/Canvas';
import { DiceRoller } from '../components/DiceRoller';
import type { GameState } from '../lib/gameEngine';
import {
  createGameState,
  rollDice,
  addLine,
  endTurn,
  getPossibleLines,
} from '../lib/gameEngine';

interface BoardProps {
  matchId: bigint;
  playerA: `0x${string}`;
  playerB: `0x${string}`;
  onGameEnd: (state: GameState) => void;
}

export function Board({ matchId, playerA, playerB, onGameEnd }: BoardProps) {
  const { address } = useAccount();

  const isPlayerA = address?.toLowerCase() === playerA.toLowerCase();
  const myRole = isPlayerA ? 'A' : 'B';

  // Initialize game with random points based on matchId
  const [gameState, setGameState] = useState<GameState>(() =>
    createGameState(playerA, playerB, matchId, 12) // 12 random points
  );

  const isMyTurn = gameState.currentTurn === myRole;
  const canDrawLine = gameState.phase === 'drawing' &&
    isMyTurn &&
    gameState.linesDrawnThisTurn < gameState.diceRoll &&
    getPossibleLines(gameState).length > 0;

  // Handle dice roll
  const handleRoll = useCallback((roll: number) => {
    setGameState(prev => rollDice(prev, roll));
  }, []);

  // Handle line drawing
  const handleLineSelect = useCallback((from: number, to: number) => {
    setGameState(prev => {
      const { state: newState, newTriangles } = addLine(prev, from, to);
      if (newTriangles.length > 0) {
        console.log(`+${newTriangles.length} triangle(s)!`);
      }
      return newState;
    });
  }, []);

  // Handle end turn
  const handleEndTurn = useCallback(() => {
    setGameState(prev => {
      const newState = endTurn(prev);
      if (newState.phase === 'finished') {
        setTimeout(() => onGameEnd(newState), 500);
      }
      return newState;
    });
  }, [onGameEnd]);

  // Check if must end turn
  const mustEndTurn = gameState.phase === 'drawing' && isMyTurn && (
    gameState.linesDrawnThisTurn >= gameState.diceRoll ||
    getPossibleLines(gameState).length === 0
  );

  // Progress info
  const maxLines = (gameState.points.length * (gameState.points.length - 1)) / 2;
  const progress = Math.round((gameState.lines.length / maxLines) * 100);

  return (
    <div className="board-page" style={{ padding: '16px', maxWidth: '600px', margin: '0 auto' }}>
      {/* Header */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
        padding: '12px 16px',
        background: 'rgba(139, 92, 246, 0.1)',
        borderRadius: '12px',
      }}>
        <div>
          <span style={{ fontSize: '14px', color: '#888' }}>Match #{matchId.toString()}</span>
          <span style={{ marginLeft: '12px', fontSize: '14px', color: '#888' }}>Turn {gameState.turnNumber}</span>
        </div>
        <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
          <span style={{ color: '#3b82f6' }}>{isPlayerA ? 'You' : 'A'}: {gameState.scoreA}</span>
          <span style={{ margin: '0 8px', color: '#888' }}>-</span>
          <span style={{ color: '#ef4444' }}>{!isPlayerA ? 'You' : 'B'}: {gameState.scoreB}</span>
        </div>
      </header>

      {/* Turn indicator */}
      <div style={{
        textAlign: 'center',
        marginBottom: '16px',
        padding: '12px',
        background: isMyTurn ? 'rgba(34, 197, 94, 0.1)' : 'rgba(251, 191, 36, 0.1)',
        borderRadius: '8px',
        border: `1px solid ${isMyTurn ? 'rgba(34, 197, 94, 0.3)' : 'rgba(251, 191, 36, 0.3)'}`,
      }}>
        <p style={{
          fontSize: '16px',
          fontWeight: 'bold',
          color: isMyTurn ? '#22c55e' : '#fbbf24',
          margin: 0,
        }}>
          {isMyTurn ? "Your Turn!" : "Opponent's Turn..."}
        </p>
      </div>

      {/* Rolling Phase */}
      {gameState.phase === 'rolling' && isMyTurn && (
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
          <p style={{ color: '#888', marginBottom: '12px' }}>Roll the dice to see how many lines you can draw</p>
          <DiceRoller onRollComplete={handleRoll} label="Roll Dice" />
        </div>
      )}

      {/* Drawing Phase Info */}
      {gameState.phase === 'drawing' && isMyTurn && (
        <div style={{
          textAlign: 'center',
          marginBottom: '16px',
          padding: '12px',
          background: 'rgba(139, 92, 246, 0.1)',
          borderRadius: '8px',
        }}>
          <p style={{ fontSize: '18px', margin: '0 0 8px 0' }}>
            Rolled: <strong style={{ color: '#a78bfa' }}>{gameState.diceRoll}</strong>
          </p>
          <p style={{ fontSize: '14px', color: '#888', margin: 0 }}>
            Lines drawn: {gameState.linesDrawnThisTurn} / {gameState.diceRoll}
          </p>
          {canDrawLine && (
            <p style={{ fontSize: '13px', color: '#a78bfa', marginTop: '8px' }}>
              Click two points to draw a line
            </p>
          )}
        </div>
      )}

      {/* Game Canvas */}
      <Canvas
        gameState={gameState}
        onLineSelect={handleLineSelect}
        isMyTurn={isMyTurn}
        canDrawLine={canDrawLine}
      />

      {/* End Turn Button */}
      {mustEndTurn && (
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <button
            onClick={handleEndTurn}
            className="btn-primary"
            style={{ padding: '12px 32px', fontSize: '16px' }}
          >
            End Turn
          </button>
        </div>
      )}

      {/* Game Stats */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-around',
        marginTop: '20px',
        padding: '16px',
        background: 'rgba(0, 0, 0, 0.2)',
        borderRadius: '12px',
      }}>
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '12px', color: '#888', margin: '0 0 4px 0' }}>Points</p>
          <p style={{ fontSize: '18px', fontWeight: 'bold', margin: 0 }}>{gameState.points.length}</p>
        </div>
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '12px', color: '#888', margin: '0 0 4px 0' }}>Lines</p>
          <p style={{ fontSize: '18px', fontWeight: 'bold', margin: 0 }}>{gameState.lines.length}/{maxLines}</p>
        </div>
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '12px', color: '#888', margin: '0 0 4px 0' }}>Triangles</p>
          <p style={{ fontSize: '18px', fontWeight: 'bold', margin: 0 }}>{gameState.triangles.length}</p>
        </div>
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '12px', color: '#888', margin: '0 0 4px 0' }}>Progress</p>
          <p style={{ fontSize: '18px', fontWeight: 'bold', margin: 0 }}>{progress}%</p>
        </div>
      </div>

      {/* Game Over */}
      {gameState.phase === 'finished' && (
        <div style={{
          marginTop: '20px',
          padding: '20px',
          background: gameState.winner === myRole ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
          borderRadius: '12px',
          textAlign: 'center',
        }}>
          <h2 style={{
            color: gameState.winner === myRole ? '#22c55e' : '#ef4444',
            margin: '0 0 8px 0',
          }}>
            {gameState.winner === myRole ? 'You Win!' :
             gameState.winner === 'draw' ? 'Draw!' :
             'You Lose!'}
          </h2>
          <p style={{ color: '#888' }}>
            Final Score: {gameState.scoreA} - {gameState.scoreB}
          </p>
        </div>
      )}
    </div>
  );
}
