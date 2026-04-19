"use client";

import { useVoice } from "@/hooks/useVoice";

interface Props {
  onTranscript: (text: string) => void;
}

export default function VoiceButton({ onTranscript }: Props) {
  const { recording, startRecording, stopRecording } = useVoice(onTranscript);

  return (
    <button
      type="button"
      onMouseDown={startRecording}
      onMouseUp={stopRecording}
      onTouchStart={startRecording}
      onTouchEnd={stopRecording}
      className="shrink-0 transition-colors text-xs px-2 py-1 rounded"
      style={{
        background: recording ? "var(--accent-dim)" : "transparent",
        color: recording ? "var(--accent)" : "var(--text-dim)",
        border: `1px solid ${recording ? "var(--accent)" : "var(--border)"}`,
      }}
      title={recording ? "release to send" : "hold to speak"}
    >
      {recording ? "● rec" : "mic"}
    </button>
  );
}
