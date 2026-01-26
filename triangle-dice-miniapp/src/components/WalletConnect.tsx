import { useAccount, useConnect, useDisconnect, useConnectors } from 'wagmi';

export function WalletConnect() {
  const { address, isConnected } = useAccount();
  const { connect, isPending } = useConnect();
  const { disconnect } = useDisconnect();
  const connectors = useConnectors();

  // Find connectors
  const coinbaseConnector = connectors.find((c) => c.id === 'coinbaseWalletSDK');
  const injectedConnector = connectors.find((c) => c.id === 'injected');

  if (isConnected && address) {
    return (
      <div className="wallet-connect connected">
        <span className="address">
          {address.slice(0, 6)}...{address.slice(-4)}
        </span>
        <button onClick={() => disconnect()} className="btn-disconnect">
          Disconnect
        </button>
      </div>
    );
  }

  const handleConnect = () => {
    if (coinbaseConnector) {
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
        {isPending ? 'Connecting...' : 'Connect Wallet'}
      </button>

      {/* Show browser wallet option if available */}
      {injectedConnector && coinbaseConnector && (
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
