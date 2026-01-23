import { EIP712_DOMAIN, EIP712_TYPES, CONTRACTS } from '../config';

export interface GameResult {
  matchId: bigint;
  finalScoreA: number;
  finalScoreB: number;
  tiebreakerRoll: number;
  winner: `0x${string}`;
  nonce: bigint;
}

// Get the domain with current contract address
export function getEIP712Domain(escrowAddress?: `0x${string}`) {
  return {
    ...EIP712_DOMAIN,
    verifyingContract: escrowAddress || (CONTRACTS.ESCROW as `0x${string}`),
  };
}

// Create typed data for signing
export function createTypedData(result: GameResult, escrowAddress?: `0x${string}`) {
  return {
    domain: getEIP712Domain(escrowAddress),
    types: EIP712_TYPES,
    primaryType: 'Result' as const,
    message: {
      matchId: result.matchId,
      finalScoreA: result.finalScoreA,
      finalScoreB: result.finalScoreB,
      tiebreakerRoll: result.tiebreakerRoll,
      winner: result.winner,
      nonce: result.nonce,
    },
  };
}

// Validate result object
export function validateResult(result: GameResult): boolean {
  if (result.matchId < 0n) return false;
  if (result.finalScoreA < 0 || result.finalScoreA > 255) return false;
  if (result.finalScoreB < 0 || result.finalScoreB > 255) return false;
  if (result.tiebreakerRoll < 0 || result.tiebreakerRoll > 6) return false;
  if (!result.winner || result.winner.length !== 42) return false;
  if (result.nonce < 0n) return false;
  return true;
}
