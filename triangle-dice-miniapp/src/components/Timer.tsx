import { useState, useEffect } from 'react';
import { GAME_CONFIG } from '../config';

interface TimerProps {
  startTime: number; // Unix timestamp
  onTimeout?: () => void;
  isPaused?: boolean;
}

export function Timer({ startTime, onTimeout, isPaused }: TimerProps) {
  const [timeLeft, setTimeLeft] = useState<number>(GAME_CONFIG.UI_TIMEOUT);

  useEffect(() => {
    if (isPaused) return;

    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() / 1000) - startTime);
      const remaining = Math.max(0, GAME_CONFIG.UI_TIMEOUT - elapsed);
      setTimeLeft(remaining);

      if (remaining === 0) {
        onTimeout?.();
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime, onTimeout, isPaused]);

  const percentage = (timeLeft / GAME_CONFIG.UI_TIMEOUT) * 100;
  const isLow = timeLeft <= 10;
  const isCritical = timeLeft <= 5;

  return (
    <div className={`timer ${isLow ? 'low' : ''} ${isCritical ? 'critical' : ''}`}>
      <div className="timer-bar">
        <div
          className="timer-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="timer-text">
        <span className="time">{timeLeft}s</span>
        <span className="label">
          (On-chain timeout: {GAME_CONFIG.ONCHAIN_TIMEOUT}s)
        </span>
      </div>
    </div>
  );
}

// Compact timer for header
export function CompactTimer({ startTime, isPaused }: { startTime: number; isPaused?: boolean }) {
  const [timeLeft, setTimeLeft] = useState<number>(GAME_CONFIG.UI_TIMEOUT);

  useEffect(() => {
    if (isPaused) return;

    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() / 1000) - startTime);
      setTimeLeft(Math.max(0, GAME_CONFIG.UI_TIMEOUT - elapsed));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime, isPaused]);

  const isLow = timeLeft <= 10;
  const isCritical = timeLeft <= 5;

  return (
    <span className={`compact-timer ${isLow ? 'low' : ''} ${isCritical ? 'critical' : ''}`}>
      ⏱️ {timeLeft}s
    </span>
  );
}
