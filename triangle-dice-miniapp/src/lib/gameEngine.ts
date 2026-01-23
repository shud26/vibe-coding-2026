/**
 * Triangle Dice Game Engine v2
 *
 * Flow:
 * 1. Game starts → Random points generated (using matchId as seed)
 * 2. Players take turns: roll dice → draw up to that many lines
 * 3. Complete triangles to score
 * 4. All lines drawn → game ends → winner takes pot
 *
 * NO transactions during gameplay - only at start and end!
 */

export interface Point {
  id: number;
  x: number;
  y: number;
}

export interface Line {
  from: number;
  to: number;
  drawnBy: 'A' | 'B';
}

export interface Triangle {
  points: [number, number, number];
  completedBy: 'A' | 'B';
}

export interface GameState {
  phase: 'rolling' | 'drawing' | 'finished';

  // Players
  playerA: string;
  playerB: string;
  currentTurn: 'A' | 'B';

  // Board
  points: Point[];
  lines: Line[];
  triangles: Triangle[];

  // Scores
  scoreA: number;
  scoreB: number;

  // Turn state
  turnNumber: number;
  diceRoll: number;
  linesDrawnThisTurn: number;

  // Result
  winner: 'A' | 'B' | 'draw' | null;
}

// Seeded random number generator (for deterministic point placement)
function seededRandom(seed: number): () => number {
  return function() {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    return seed / 0x7fffffff;
  };
}

// Generate random points based on match ID
export function generateRandomPoints(matchId: bigint, count: number, boardSize: number, padding: number): Point[] {
  const seed = Number(matchId % BigInt(2147483647));
  const random = seededRandom(seed);

  const points: Point[] = [];
  const minDistance = 40; // Minimum distance between points
  const usableSize = boardSize - (padding * 2);

  let attempts = 0;
  while (points.length < count && attempts < 1000) {
    const x = padding + random() * usableSize;
    const y = padding + random() * usableSize;

    // Check distance from existing points
    const tooClose = points.some(p =>
      Math.hypot(p.x - x, p.y - y) < minDistance
    );

    if (!tooClose) {
      points.push({ id: points.length, x, y });
    }
    attempts++;
  }

  return points;
}

// Create initial game state
export function createGameState(
  playerA: string,
  playerB: string,
  matchId: bigint,
  pointCount: number = 12,
  boardSize: number = 500,
  padding: number = 40
): GameState {
  const points = generateRandomPoints(matchId, pointCount, boardSize, padding);

  return {
    phase: 'rolling',
    playerA,
    playerB,
    currentTurn: 'A',
    points,
    lines: [],
    triangles: [],
    scoreA: 0,
    scoreB: 0,
    turnNumber: 1,
    diceRoll: 0,
    linesDrawnThisTurn: 0,
    winner: null,
  };
}

// Normalize line (smaller ID first)
function normalizeLine(from: number, to: number): { from: number; to: number } {
  return from < to ? { from, to } : { from: to, to: from };
}

// Check if line exists
export function lineExists(lines: Line[], from: number, to: number): boolean {
  const n = normalizeLine(from, to);
  return lines.some(l => {
    const ln = normalizeLine(l.from, l.to);
    return ln.from === n.from && ln.to === n.to;
  });
}

// Add a line and detect new triangles
export function addLine(
  state: GameState,
  from: number,
  to: number
): { state: GameState; newTriangles: Triangle[] } {
  if (from === to) return { state, newTriangles: [] };
  if (lineExists(state.lines, from, to)) return { state, newTriangles: [] };
  if (state.linesDrawnThisTurn >= state.diceRoll) return { state, newTriangles: [] };

  const normalized = normalizeLine(from, to);
  const newLine: Line = {
    from: normalized.from,
    to: normalized.to,
    drawnBy: state.currentTurn
  };
  const newLines = [...state.lines, newLine];

  // Find new triangles
  const newTriangles: Triangle[] = [];

  for (const point of state.points) {
    if (point.id === from || point.id === to) continue;

    // Check if triangle is formed
    const edge1 = lineExists(newLines, from, point.id);
    const edge2 = lineExists(newLines, to, point.id);

    if (edge1 && edge2) {
      const triPoints = [from, to, point.id].sort((a, b) => a - b) as [number, number, number];

      // Check if already counted
      const exists = state.triangles.some(t =>
        t.points[0] === triPoints[0] &&
        t.points[1] === triPoints[1] &&
        t.points[2] === triPoints[2]
      );

      if (!exists) {
        newTriangles.push({
          points: triPoints,
          completedBy: state.currentTurn,
        });
      }
    }
  }

  const newState: GameState = {
    ...state,
    lines: newLines,
    triangles: [...state.triangles, ...newTriangles],
    linesDrawnThisTurn: state.linesDrawnThisTurn + 1,
    scoreA: state.scoreA + (state.currentTurn === 'A' ? newTriangles.length : 0),
    scoreB: state.scoreB + (state.currentTurn === 'B' ? newTriangles.length : 0),
  };

  return { state: newState, newTriangles };
}

// Get all possible lines
export function getPossibleLines(state: GameState): { from: number; to: number }[] {
  const possible: { from: number; to: number }[] = [];

  for (let i = 0; i < state.points.length; i++) {
    for (let j = i + 1; j < state.points.length; j++) {
      if (!lineExists(state.lines, state.points[i].id, state.points[j].id)) {
        possible.push({ from: state.points[i].id, to: state.points[j].id });
      }
    }
  }

  return possible;
}

// Check if all lines are drawn
export function isGameOver(state: GameState): boolean {
  const maxLines = (state.points.length * (state.points.length - 1)) / 2;
  return state.lines.length >= maxLines;
}

// Roll dice and start drawing phase
export function rollDice(state: GameState, roll: number): GameState {
  return {
    ...state,
    phase: 'drawing',
    diceRoll: roll,
    linesDrawnThisTurn: 0,
  };
}

// End turn
export function endTurn(state: GameState): GameState {
  // Check game over
  if (isGameOver(state)) {
    let winner: 'A' | 'B' | 'draw' | null = null;
    if (state.scoreA > state.scoreB) winner = 'A';
    else if (state.scoreB > state.scoreA) winner = 'B';
    else winner = 'draw';

    return {
      ...state,
      phase: 'finished',
      winner,
    };
  }

  // Switch turn
  return {
    ...state,
    phase: 'rolling',
    currentTurn: state.currentTurn === 'A' ? 'B' : 'A',
    turnNumber: state.turnNumber + 1,
    diceRoll: 0,
    linesDrawnThisTurn: 0,
  };
}

// For contract submission
export function getGameResult(state: GameState): {
  finalScoreA: number;
  finalScoreB: number;
  winner: string;
} {
  return {
    finalScoreA: state.scoreA,
    finalScoreB: state.scoreB,
    winner: state.winner === 'A' ? state.playerA :
            state.winner === 'B' ? state.playerB :
            '0x0000000000000000000000000000000000000000',
  };
}
