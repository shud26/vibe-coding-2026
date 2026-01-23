// Mini App Configuration for Triangle Dice
// This configuration is used for Farcaster/Base Mini App integration

export const MINIKIT_CONFIG = {
  // App metadata
  name: 'Triangle Dice',
  description: '1v1 betting game - complete triangles to win!',
  category: 'games',

  // URLs (update with your actual deployed URL)
  appUrl: 'https://triangle-dice-miniapp.vercel.app',
  iconUrl: 'https://triangle-dice-miniapp.vercel.app/assets/icon.png',
  splashImageUrl: 'https://triangle-dice-miniapp.vercel.app/assets/splash.png',
  previewImageUrl: 'https://triangle-dice-miniapp.vercel.app/assets/preview.png',

  // Theme
  splashBackgroundColor: '#0B0B0F',

  // Frame settings
  buttonTitle: 'Play',
  version: '1',

  // Account Association (to be filled after registering at base.dev)
  // You need to:
  // 1. Go to base.dev/build
  // 2. Connect your wallet and sign the account association message
  // 3. Copy the header, payload, and signature values here
  accountAssociation: {
    header: '__REPLACE_ME__ACCOUNT_ASSOCIATION_HEADER__',
    payload: '__REPLACE_ME__ACCOUNT_ASSOCIATION_PAYLOAD__',
    signature: '__REPLACE_ME__ACCOUNT_ASSOCIATION_SIGNATURE__',
  },
} as const;

// Generate farcaster.json content from config
export function generateFarcasterJson() {
  return {
    accountAssociation: MINIKIT_CONFIG.accountAssociation,
    frame: {
      version: MINIKIT_CONFIG.version,
      name: MINIKIT_CONFIG.name,
      iconUrl: MINIKIT_CONFIG.iconUrl,
      homeUrl: MINIKIT_CONFIG.appUrl,
      imageUrl: MINIKIT_CONFIG.previewImageUrl,
      buttonTitle: MINIKIT_CONFIG.buttonTitle,
      splashImageUrl: MINIKIT_CONFIG.splashImageUrl,
      splashBackgroundColor: MINIKIT_CONFIG.splashBackgroundColor,
    },
  };
}
