"use client";

import { useEffect, useRef } from "react";

interface Props {
  active: boolean;
  stream: MediaStream | null;
}

export default function AudioVisualizer({ active, stream }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    if (!active || !stream) return;

    const audioCtx = new AudioContext();
    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 64;
    const source = audioCtx.createMediaStreamSource(stream);
    source.connect(analyser);

    const buffer = new Uint8Array(analyser.frequencyBinCount);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;

    const draw = () => {
      analyser.getByteFrequencyData(buffer);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const barWidth = canvas.width / buffer.length;
      buffer.forEach((value, i) => {
        const height = (value / 255) * canvas.height;
        ctx.fillStyle = `rgba(59,130,246,${value / 255})`;
        ctx.fillRect(i * barWidth, canvas.height - height, barWidth - 1, height);
      });
      rafRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(rafRef.current);
      source.disconnect();
      audioCtx.close();
    };
  }, [active, stream]);

  return (
    <canvas
      ref={canvasRef}
      width={200}
      height={40}
      className={`rounded transition-opacity ${active ? "opacity-100" : "opacity-0"}`}
    />
  );
}
