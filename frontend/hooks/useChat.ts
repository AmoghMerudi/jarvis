"use client";

import { useState, useCallback } from "react";
import { sendMessage, type Message } from "@/lib/api";

export function useChat() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<Message[]>([]);

  const send = useCallback(async (text: string): Promise<string | null> => {
    setError(null);
    setLoading(true);

    try {
      const reply = await sendMessage(text, history);
      const userMsg: Message = { role: "user", content: text };
      const assistantMsg: Message = { role: "assistant", content: reply };
      setHistory((prev) => [...prev, userMsg, assistantMsg]);
      return reply;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "unknown error";
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, [history]);

  return { loading, error, send };
}
