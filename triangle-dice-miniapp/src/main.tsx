import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';

// Check if running inside Mini App context
const isMiniApp = () => {
  try {
    return window.parent !== window ||
           window.location.search.includes('fc_') ||
           document.referrer.includes('warpcast') ||
           document.referrer.includes('base.org');
  } catch {
    return false;
  }
};

// Initialize Mini App SDK if in Mini App context
if (isMiniApp()) {
  import('@farcaster/miniapp-sdk').then((module) => {
    try {
      module.default.actions.ready();
      console.log('Farcaster SDK ready() called');
    } catch (e) {
      console.log('Farcaster SDK init error:', e);
    }
  }).catch((e) => {
    console.log('Failed to load Farcaster SDK:', e);
  });
} else {
  console.log('Running in web browser mode');
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
