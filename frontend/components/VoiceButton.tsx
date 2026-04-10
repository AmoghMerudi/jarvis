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
      className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
        recording
          ? "bg-red-600 hover:bg-red-500"
          : "bg-gray-700 hover:bg-gray-600"
      }`}
      title={recording ? "Release to send" : "Hold to speak"}
    >
      {recording ? "●" : "🎙"}
    </button>
  );
}
