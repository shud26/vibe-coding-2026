import { useAccount, useConnect, useDisconnect, useConnectors } from 'wagmi';
import { useMiniKit, useIsInMiniApp } from '@coinbase/onchainkit/minikit';

export function WalletConnect() {
  const { address, isConnected } = useAccount();
  const { connect, isPending } = useConnect();
  const { disconnect } = useDisconnect();
  const connectors = useConnectors();
  const { context } = useMiniKit();
  const isInMiniApp = useIsInMiniApp();

  // Find Coinbase Wallet connector (preferred for Mini Apps)
  const coinbaseConnector = connectors.find((c) => c.id === 'coinbaseWalletSDK');
  const injectedConnector = connectors.find((c) => c.id === 'injected');

  // Show Farcaster user info if available
  const farcasterUser = context?.user;

  if (isConnected && address) {
    return (
      <div className="wallet-connect connected">
        {farcasterUser && (
          <span className="farcaster-user" style={{ marginRight: '8px', color: '#a78bfa' }}>
            @{farcasterUser.username || 'farcaster'}
          </span>
        )}
        <span className="address">
          {address.slice(0, 6)}...{address.slice(-4)}
        </span>
        <button onClick={() => disconnect()} className="btn-disconnect">
          Disconnect
        </button>
      </div>
    );
  }

  // In Mini App environment, prefer Coinbase Wallet
  const handleConnect = () => {
    if (isInMiniApp && coinbaseConnector) {
      connect({ connector: coinbaseConnector });
    } else if (coinbaseConnector) {
      connect({ connector: coinbaseConnector });
    } else if (injectedConnector) {
      connect({ connector: injectedConnector });
    }
  };

  return (
    <div className="wallet-connect-buttons">
      <button
        onClick={handleConnect}
        disabled={isPending}
        className="btn-connect"
      >
        {isPending ? 'Connecting...' : isInMiniApp ? 'Connect Wallet' : 'Connect Coinbase Wallet'}
      </button>

      {/* Show injected option if not in Mini App and both connectors exist */}
      {!isInMiniApp && injectedConnector && coinbaseConnector && (
        <button
          onClick={() => connect({ connector: injectedConnector })}
          disabled={isPending}
          className="btn-connect-secondary"
          style={{ marginLeft: '8px' }}
        >
          Browser Wallet
        </button>
      )}
    </div>
  );
}
