import { useReadContract, useWriteContract, useWaitForTransactionReceipt } from 'wagmi';
import { CONTRACTS } from '../config';
import escrowAbi from '../abi/TriangleDiceEscrow.json';
import usdcAbi from '../abi/MockUSDC.json';
import type { GameResult } from '../lib/eip712';

// Match status constants matching contract
export const MatchStatus = {
  None: 0,
  Created: 1,
  Joined: 2,
  Started: 3,
  Settled: 4,
  Cancelled: 5,
  TimeoutClaimed: 6,
} as const;

export type MatchStatus = typeof MatchStatus[keyof typeof MatchStatus];

export interface Match {
  playerA: `0x${string}`;
  playerB: `0x${string}`;
  stakeAmount: bigint;
  timeoutSec: bigint;
  lastActivity: bigint;
  status: MatchStatus;
  nonce: bigint;
}

// Read match data
export function useMatch(matchId: bigint | null) {
  const isValidMatchId = matchId !== null && matchId >= 1n;
  console.log('useMatch called with:', matchId?.toString(), 'isValid:', isValidMatchId);
  return useReadContract({
    address: CONTRACTS.ESCROW as `0x${string}`,
    abi: escrowAbi,
    functionName: 'getMatch',
    args: isValidMatchId ? [matchId] : undefined,
    query: { enabled: isValidMatchId },
  });
}

// Read time remaining
export function useTimeRemaining(matchId: bigint) {
  return useReadContract({
    address: CONTRACTS.ESCROW as `0x${string}`,
    abi: escrowAbi,
    functionName: 'getTimeRemaining',
    args: [matchId],
  });
}

// Read USDC balance
export function useUSDCBalance(address: `0x${string}` | undefined) {
  return useReadContract({
    address: CONTRACTS.USDC as `0x${string}`,
    abi: usdcAbi,
    functionName: 'balanceOf',
    args: address ? [address] : undefined,
    query: { enabled: !!address },
  });
}

// Read USDC allowance
export function useUSDCAllowance(owner: `0x${string}` | undefined) {
  return useReadContract({
    address: CONTRACTS.USDC as `0x${string}`,
    abi: usdcAbi,
    functionName: 'allowance',
    args: owner ? [owner, CONTRACTS.ESCROW as `0x${string}`] : undefined,
    query: { enabled: !!owner },
  });
}

// Write hooks
export function useApproveUSDC() {
  const { writeContract, data: hash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash });

  const approve = (amount: bigint) => {
    writeContract({
      address: CONTRACTS.USDC as `0x${string}`,
      abi: usdcAbi,
      functionName: 'approve',
      args: [CONTRACTS.ESCROW as `0x${string}`, amount],
    });
  };

  return { approve, hash, isPending, isConfirming, isSuccess, error };
}

export function useCreateMatch() {
  const { writeContract, data: hash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess, data: receipt } = useWaitForTransactionReceipt({ hash });

  const createMatch = (stakeAmount: bigint, timeoutSec: bigint) => {
    writeContract({
      address: CONTRACTS.ESCROW as `0x${string}`,
      abi: escrowAbi,
      functionName: 'createMatch',
      args: [stakeAmount, timeoutSec],
    });
  };

  return { createMatch, hash, isPending, isConfirming, isSuccess, receipt, error };
}

export function useJoinMatch() {
  const { writeContract, data: hash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess, data: receipt } = useWaitForTransactionReceipt({ hash });

  const joinMatch = (matchId: bigint) => {
    console.log('=== JOIN MATCH ===');
    console.log('Contract:', CONTRACTS.ESCROW);
    console.log('MatchId:', matchId.toString());

    writeContract({
      address: CONTRACTS.ESCROW as `0x${string}`,
      abi: escrowAbi,
      functionName: 'joinMatch',
      args: [matchId],
    });
  };

  // Log any errors
  if (error) {
    console.error('Join error:', error);
  }
  if (hash) {
    console.log('Join tx hash:', hash);
  }

  return { joinMatch, hash, isPending, isConfirming, isSuccess, receipt, error };
}

export function useStartMatch() {
  const { writeContract, data: hash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash });

  const startMatch = (matchId: bigint) => {
    writeContract({
      address: CONTRACTS.ESCROW as `0x${string}`,
      abi: escrowAbi,
      functionName: 'startMatch',
      args: [matchId],
    });
  };

  return { startMatch, hash, isPending, isConfirming, isSuccess, error };
}

export function usePing() {
  const { writeContract, data: hash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash });

  const ping = (matchId: bigint) => {
    writeContract({
      address: CONTRACTS.ESCROW as `0x${string}`,
      abi: escrowAbi,
      functionName: 'ping',
      args: [matchId],
    });
  };

  return { ping, hash, isPending, isConfirming, isSuccess, error };
}

export function useClaimTimeoutWin() {
  const { writeContract, data: hash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash });

  const claimTimeoutWin = (matchId: bigint) => {
    writeContract({
      address: CONTRACTS.ESCROW as `0x${string}`,
      abi: escrowAbi,
      functionName: 'claimTimeoutWin',
      args: [matchId],
    });
  };

  return { claimTimeoutWin, hash, isPending, isConfirming, isSuccess, error };
}

export function useCancelMatch() {
  const { writeContract, data: hash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash });

  const cancelMatch = (matchId: bigint) => {
    writeContract({
      address: CONTRACTS.ESCROW as `0x${string}`,
      abi: escrowAbi,
      functionName: 'cancelIfNotJoined',
      args: [matchId],
    });
  };

  return { cancelMatch, hash, isPending, isConfirming, isSuccess, error };
}

export function useSubmitResult() {
  const { writeContract, data: hash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash });

  const submitResult = (result: GameResult, sigA: `0x${string}`, sigB: `0x${string}`) => {
    writeContract({
      address: CONTRACTS.ESCROW as `0x${string}`,
      abi: escrowAbi,
      functionName: 'submitResult',
      args: [
        {
          matchId: result.matchId,
          finalScoreA: result.finalScoreA,
          finalScoreB: result.finalScoreB,
          tiebreakerRoll: result.tiebreakerRoll,
          winner: result.winner,
          nonce: result.nonce,
        },
        sigA,
        sigB,
      ],
    });
  };

  return { submitResult, hash, isPending, isConfirming, isSuccess, error };
}

// Mint test USDC (only works with MockUSDC)
export function useMintUSDC() {
  const { writeContract, data: hash, isPending, error } = useWriteContract();
  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({ hash });

  const mint = (to: `0x${string}`, amount: bigint) => {
    writeContract({
      address: CONTRACTS.USDC as `0x${string}`,
      abi: usdcAbi,
      functionName: 'mint',
      args: [to, amount],
    });
  };

  return { mint, hash, isPending, isConfirming, isSuccess, error };
}
