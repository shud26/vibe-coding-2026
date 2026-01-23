import { useState, useEffect } from 'react';
import { WagmiProvider } from 'wagmi';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useMiniKit } from '@coinbase/onchainkit/minikit';
import sdk from '@farcaster/miniapp-sdk';
import { wagmiConfig } from './config';
import { Lobby } from './pages/Lobby';
import { Board } from './pages/Board';
import { Result } from './pages/Result';
import type { GameState } from './lib/gameEngine';
import './App.css';

const queryClient = new QueryClient();

type Screen = 'lobby' | 'board' | 'result';

interface MatchInfo {
  matchId: bigint;
  playerA: `0x${string}`;
  playerB: `0x${string}`;
}

function AppContent() {
  const [screen, setScreen] = useState<Screen>('lobby');
  const [matchInfo, setMatchInfo] = useState<MatchInfo | null>(null);
  const [finalGameState, setFinalGameState] = useState<GameState | null>(null);

  // MiniKit integration
  const { setFrameReady, isFrameReady, context } = useMiniKit();

  // Signal to Farcaster/Base that the app is ready - using official SDK
  useEffect(() => {
    // Use official Farcaster SDK
    sdk.actions.ready();
    console.log('Farcaster SDK ready() called');

    // Also try OnchainKit method
    if (!isFrameReady) {
      setFrameReady();
    }
  }, [setFrameReady, isFrameReady]);

  // Log context for debugging (Farcaster user info available here)
  useEffect(() => {
    if (context) {
      console.log('MiniKit context:', context);
    }
  }, [context]);

  const handleMatchCreated = (matchId: bigint) => {
    // In real implementation, would get this from contract event
    // For now, user needs to share matchId manually
    console.log('Match created:', matchId);
  };

  const handleMatchJoined = (matchId: bigint) => {
    // Would transition to board after host starts
    console.log('Joined match:', matchId);
  };

  const handleStartGame = (info: MatchInfo) => {
    setMatchInfo(info);
    setScreen('board');
  };

  const handleGameEnd = (state: GameState) => {
    setFinalGameState(state);
    setScreen('result');
  };

  const handleBackToLobby = () => {
    setScreen('lobby');
    setMatchInfo(null);
    setFinalGameState(null);
  };

  return (
    <div className="app">
      {screen === 'lobby' && (
        <Lobby
          onMatchCreated={handleMatchCreated}
          onMatchJoined={handleMatchJoined}
          onGameStart={(matchId, playerA, playerB) => {
            handleStartGame({ matchId, playerA, playerB });
          }}
        />
      )}

      {screen === 'board' && matchInfo && (
        <Board
          matchId={matchInfo.matchId}
          playerA={matchInfo.playerA}
          playerB={matchInfo.playerB}
          onGameEnd={handleGameEnd}
        />
      )}

      {screen === 'result' && matchInfo && finalGameState && (
        <Result
          matchId={matchInfo.matchId}
          gameState={finalGameState}
          onBackToLobby={handleBackToLobby}
        />
      )}

      {/* Dev Tools - remove in production */}
      {import.meta.env.DEV && (
        <div className="dev-tools">
          <button onClick={() => setScreen('lobby')}>Lobby</button>
          <button
            onClick={() =>
              handleStartGame({
                matchId: 1n,
                playerA: '0x1234567890123456789012345678901234567890' as `0x${string}`,
                playerB: '0x0987654321098765432109876543210987654321' as `0x${string}`,
              })
            }
          >
            Test Game
          </button>
        </div>
      )}
    </div>
  );
}

export default function App() {
  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        <AppContent />
      </QueryClientProvider>
    </WagmiProvider>
  );
}
