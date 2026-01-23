import { keccak256, encodePacked, toHex } from 'viem';

/**
 * Dice Commit-Reveal Scheme
 *
 * 1. Player commits: hash(roll + salt)
 * 2. Other player commits their hash
 * 3. Both reveal: roll + salt
 * 4. Verify commitments match
 * 5. Determine winner
 */

export interface DiceCommit {
  hash: `0x${string}`;
  roll?: number;
  salt?: `0x${string}`;
}

// Generate a random salt (32 bytes)
export function generateSalt(): `0x${string}` {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return toHex(array);
}

// Roll a dice (1-6)
export function rollDice(): number {
  return Math.floor(Math.random() * 6) + 1;
}

// Create a commitment hash
export function createCommitment(roll: number, salt: `0x${string}`): `0x${string}` {
  return keccak256(encodePacked(['uint8', 'bytes32'], [roll, salt]));
}

// Verify a commitment
export function verifyCommitment(
  commitment: `0x${string}`,
  roll: number,
  salt: `0x${string}`
): boolean {
  const expectedHash = createCommitment(roll, salt);
  return commitment.toLowerCase() === expectedHash.toLowerCase();
}

// Create a new dice roll with commitment
export function createDiceRoll(): { roll: number; salt: `0x${string}`; commitment: `0x${string}` } {
  const roll = rollDice();
  const salt = generateSalt();
  const commitment = createCommitment(roll, salt);
  return { roll, salt, commitment };
}

// Combine two dice rolls to get a result
// XOR the values and mod 6 + 1 for unpredictability
export function combineDiceRolls(rollA: number, rollB: number): number {
  return ((rollA + rollB - 2) % 6) + 1;
}

// Determine winner of dice roll
export function getDiceWinner(rollA: number, rollB: number): 'A' | 'B' | 'tie' {
  if (rollA > rollB) return 'A';
  if (rollB > rollA) return 'B';
  return 'tie';
}
