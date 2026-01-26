import { baseSepolia } from 'wagmi/chains';
import { http, createConfig, createStorage } from 'wagmi';
import { coinbaseWallet, injected } from 'wagmi/connectors';

// Contract addresses on Base Sepolia
export const CONTRACTS = {
  USDC: '0x2aC28e4754a9Eeae143399fC1B0B1F9bBe9E2CC3',
  ESCROW: '0x0e6Bb9F887B3ca03d942558FaB935701C5A44f21',
} as const;

// Chain config
export const CHAIN = baseSepolia;
export const CHAIN_ID = CHAIN.id;

// App URL
export const APP_URL = import.meta.env.VITE_APP_URL || 'https://triangle-dice-miniapp.vercel.app';

// Wagmi config for Mini App (Coinbase Wallet + injected)
export const wagmiConfig = createConfig({
  chains: [baseSepolia],
  connectors: [
    coinbaseWallet({
      appName: 'Triangle Dice',
      appLogoUrl: `${APP_URL}/assets/icon.png`,
      preference: 'smartWalletOnly', // For Mini Apps, prefer smart wallet
    }),
    injected(),
  ],
  storage: createStorage({ storage: localStorage }),
  transports: {
    [baseSepolia.id]: http(import.meta.env.VITE_RPC_URL || 'https://sepolia.base.org'),
  },
});

// Game constants
export const GAME_CONFIG = {
  MIN_STAKE: 0.5, // USDC
  MAX_STAKE: 10, // USDC
  USDC_DECIMALS: 6,
  MIN_POINTS: 8,
  MAX_POINTS: 20,
  ONCHAIN_TIMEOUT: 90, // seconds
  UI_TIMEOUT: 30, // seconds (displayed to user)
  DICE_MIN: 1,
  DICE_MAX: 6,
} as const;

// EIP-712 domain
export const EIP712_DOMAIN = {
  name: 'TriangleDiceEscrow',
  version: '1',
  chainId: CHAIN_ID,
  verifyingContract: CONTRACTS.ESCROW as `0x${string}`,
} as const;

// EIP-712 types
export const EIP712_TYPES = {
  Result: [
    { name: 'matchId', type: 'uint256' },
    { name: 'finalScoreA', type: 'uint8' },
    { name: 'finalScoreB', type: 'uint8' },
    { name: 'tiebreakerRoll', type: 'uint8' },
    { name: 'winner', type: 'address' },
    { name: 'nonce', type: 'uint256' },
  ],
} as const;

// Helper to convert USDC amount to contract units (6 decimals)
export function toUSDCUnits(amount: number): bigint {
  return BigInt(Math.floor(amount * 10 ** GAME_CONFIG.USDC_DECIMALS));
}

// Helper to convert contract units to USDC amount
export function fromUSDCUnits(units: bigint): number {
  return Number(units) / 10 ** GAME_CONFIG.USDC_DECIMALS;
}
