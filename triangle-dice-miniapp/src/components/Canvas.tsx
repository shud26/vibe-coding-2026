import { useRef, useEffect, useState } from 'react';
import type { GameState, Point, Line, Triangle } from '../lib/gameEngine';

interface CanvasProps {
  gameState: GameState;
  onLineSelect?: (from: number, to: number) => void;
  isMyTurn: boolean;
  canDrawLine: boolean;
}

const CANVAS_SIZE = 500; // Bigger board!
const POINT_RADIUS = 12;

export function Canvas({
  gameState,
  onLineSelect,
  isMyTurn,
  canDrawLine,
}: CanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedPoint, setSelectedPoint] = useState<number | null>(null);
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);

  // Draw the game board
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas with dark background
    ctx.fillStyle = '#0f0f1a';
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

    // Draw subtle grid
    ctx.strokeStyle = '#1a1a2e';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 10; i++) {
      const pos = (i * CANVAS_SIZE) / 10;
      ctx.beginPath();
      ctx.moveTo(pos, 0);
      ctx.lineTo(pos, CANVAS_SIZE);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, pos);
      ctx.lineTo(CANVAS_SIZE, pos);
      ctx.stroke();
    }

    // Draw completed triangles (filled)
    gameState.triangles.forEach((triangle: Triangle) => {
      const p1 = gameState.points.find((p: Point) => p.id === triangle.points[0]);
      const p2 = gameState.points.find((p: Point) => p.id === triangle.points[1]);
      const p3 = gameState.points.find((p: Point) => p.id === triangle.points[2]);

      if (p1 && p2 && p3) {
        // Player A = blue, Player B = red
        ctx.fillStyle = triangle.completedBy === 'A'
          ? 'rgba(59, 130, 246, 0.3)'
          : 'rgba(239, 68, 68, 0.3)';
        ctx.strokeStyle = triangle.completedBy === 'A'
          ? 'rgba(59, 130, 246, 0.8)'
          : 'rgba(239, 68, 68, 0.8)';
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.lineTo(p3.x, p3.y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      }
    });

    // Draw existing lines
    gameState.lines.forEach((line: Line) => {
      const from = gameState.points.find((p: Point) => p.id === line.from);
      const to = gameState.points.find((p: Point) => p.id === line.to);

      if (from && to) {
        ctx.strokeStyle = line.drawnBy === 'A' ? '#3b82f6' : '#ef4444';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        ctx.stroke();
      }
    });

    // Draw line preview (dashed)
    if (selectedPoint !== null && hoveredPoint !== null && selectedPoint !== hoveredPoint) {
      const from = gameState.points.find((p: Point) => p.id === selectedPoint);
      const to = gameState.points.find((p: Point) => p.id === hoveredPoint);

      if (from && to) {
        ctx.strokeStyle = 'rgba(168, 85, 247, 0.7)';
        ctx.lineWidth = 3;
        ctx.setLineDash([8, 8]);
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // Draw points
    gameState.points.forEach((point: Point) => {
      const isSelected = selectedPoint === point.id;
      const isHovered = hoveredPoint === point.id;

      // Outer glow for selected/hovered
      if (isSelected || isHovered) {
        ctx.beginPath();
        ctx.arc(point.x, point.y, POINT_RADIUS + 6, 0, Math.PI * 2);
        ctx.fillStyle = isSelected ? 'rgba(34, 197, 94, 0.3)' : 'rgba(168, 85, 247, 0.3)';
        ctx.fill();
      }

      // Main point
      ctx.beginPath();
      ctx.arc(point.x, point.y, POINT_RADIUS, 0, Math.PI * 2);

      // Gradient fill
      const gradient = ctx.createRadialGradient(
        point.x - 3, point.y - 3, 0,
        point.x, point.y, POINT_RADIUS
      );
      if (isSelected) {
        gradient.addColorStop(0, '#4ade80');
        gradient.addColorStop(1, '#22c55e');
      } else if (isHovered) {
        gradient.addColorStop(0, '#c084fc');
        gradient.addColorStop(1, '#a855f7');
      } else {
        gradient.addColorStop(0, '#f1f5f9');
        gradient.addColorStop(1, '#cbd5e1');
      }

      ctx.fillStyle = gradient;
      ctx.fill();

      // Border
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Point number
      ctx.fillStyle = '#1e293b';
      ctx.font = 'bold 11px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(String(point.id + 1), point.x, point.y);
    });
  }, [gameState, selectedPoint, hoveredPoint]);

  // Handle click
  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canDrawLine || !isMyTurn) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = CANVAS_SIZE / rect.width;
    const scaleY = CANVAS_SIZE / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    // Find clicked point
    const clickedPoint = gameState.points.find(
      (p: Point) => Math.hypot(p.x - x, p.y - y) < POINT_RADIUS * 2
    );

    if (clickedPoint) {
      if (selectedPoint === null) {
        setSelectedPoint(clickedPoint.id);
      } else if (selectedPoint !== clickedPoint.id) {
        onLineSelect?.(selectedPoint, clickedPoint.id);
        setSelectedPoint(null);
      } else {
        setSelectedPoint(null);
      }
    }
  };

  // Handle mouse move
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = CANVAS_SIZE / rect.width;
    const scaleY = CANVAS_SIZE / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    const hovered = gameState.points.find(
      (p: Point) => Math.hypot(p.x - x, p.y - y) < POINT_RADIUS * 2
    );

    setHoveredPoint(hovered?.id ?? null);
  };

  return (
    <div className="canvas-container" style={{ width: '100%', maxWidth: '500px', margin: '0 auto' }}>
      <canvas
        ref={canvasRef}
        width={CANVAS_SIZE}
        height={CANVAS_SIZE}
        onClick={handleClick}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => {
          setHoveredPoint(null);
        }}
        style={{
          width: '100%',
          height: 'auto',
          borderRadius: '12px',
          cursor: isMyTurn && canDrawLine ? 'crosshair' : 'default',
          boxShadow: '0 0 40px rgba(139, 92, 246, 0.2)',
        }}
      />
      {selectedPoint !== null && (
        <p style={{ textAlign: 'center', color: '#a78bfa', marginTop: '8px', fontSize: '14px' }}>
          Point {selectedPoint + 1} selected - click another point to draw a line
        </p>
      )}
    </div>
  );
}
