"use client";

import { useState, useRef, useEffect, useCallback, KeyboardEvent } from "react";
import { useChat } from "@/hooks/useChat";
import VoiceButton from "@/components/VoiceButton";
import { type Message } from "@/lib/api";

function formatTime(date: Date) {
  return date.toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

interface TimestampedMessage extends Message {
  ts: Date;
}

export default function Chat() {
  const { loading, send } = useChat();
  const [messages, setMessages] = useState<TimestampedMessage[]>([]);
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [histIdx, setHistIdx] = useState(-1);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setHistory((h) => [trimmed, ...h]);
    setHistIdx(-1);
    setInput("");

    const userMsg: TimestampedMessage = { role: "user", content: trimmed, ts: new Date() };
    setMessages((prev) => [...prev, userMsg]);

    const reply = await send(trimmed);
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: reply ?? "[error] request failed",
        ts: new Date(),
      },
    ]);
  }, [loading, send]);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      const next = Math.min(histIdx + 1, history.length - 1);
      setHistIdx(next);
      setInput(history[next] ?? "");
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      const next = Math.max(histIdx - 1, -1);
      setHistIdx(next);
      setInput(next === -1 ? "" : history[next]);
    }
    if (e.key === "l" && e.ctrlKey) {
      e.preventDefault();
      setMessages([]);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* topbar */}
      <div
        className="flex items-center justify-between px-4 py-2 shrink-0 border-b"
        style={{ borderColor: "var(--border)", background: "var(--surface)" }}
      >
        <div className="flex items-center gap-3">
          <span className="text-xs" style={{ color: "var(--text-dim)" }}>
            agent:loop
          </span>
          <span className="text-xs px-1.5 py-0.5 rounded" style={{ background: "var(--border)", color: "var(--text-dim)" }}>
            {messages.length} msg{messages.length !== 1 ? "s" : ""}
          </span>
        </div>
        <button
          onClick={() => setMessages([])}
          className="text-xs transition-colors"
          style={{ color: "var(--text-muted)" }}
          onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text)")}
          onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-muted)")}
          title="Clear (Ctrl+L)"
        >
          clear
        </button>
      </div>

      {/* message log */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
        {messages.length === 0 && (
          <div className="flex flex-col gap-2 mt-12 px-1">
            <p className="text-sm" style={{ color: "var(--accent)" }}>
              jarvis <span style={{ color: "var(--text-dim)" }}>ready.</span>
            </p>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              type a command or hold mic to speak.
            </p>
            <div className="mt-4 space-y-1">
              {["what can you do?", "what time is it?", "remember that I prefer dark mode"].map((hint) => (
                <p
                  key={hint}
                  className="text-xs cursor-pointer transition-colors"
                  style={{ color: "var(--text-muted)" }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = "var(--text-dim)")}
                  onMouseLeave={(e) => (e.currentTarget.style.color = "var(--text-muted)")}
                  onClick={() => { setInput(hint); inputRef.current?.focus(); }}
                >
                  › {hint}
                </p>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) =>
          msg.role === "user" ? (
            <UserLine key={idx} msg={msg} />
          ) : (
            <AssistantBlock key={idx} msg={msg} />
          )
        )}

        {loading && <ThinkingLine />}

        <div ref={bottomRef} />
      </div>

      {/* input */}
      <div
        className="shrink-0 border-t px-4 py-3"
        style={{ borderColor: "var(--border)", background: "var(--surface)" }}
      >
        <div className="flex items-center gap-3">
          <span className="text-sm select-none" style={{ color: "var(--accent)" }}>
            ❯
          </span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="enter command…"
            autoFocus
            className="flex-1 bg-transparent outline-none text-sm placeholder-[var(--text-muted)]"
            style={{ color: "var(--text)", caretColor: "var(--accent)" }}
            spellCheck={false}
            autoComplete="off"
          />
          <VoiceButton
            onTranscript={(text) => {
              setInput("");
              handleSend(text);
            }}
          />
        </div>
      </div>
    </div>
  );
}

function UserLine({ msg }: { msg: TimestampedMessage }) {
  return (
    <div className="flex items-start gap-3 group py-0.5">
      <span className="text-xs shrink-0 tabular-nums mt-0.5" style={{ color: "var(--text-muted)" }}>
        {formatTime(msg.ts)}
      </span>
      <span className="text-xs shrink-0 mt-0.5" style={{ color: "var(--user-color)" }}>
        you
      </span>
      <span className="text-sm" style={{ color: "var(--text)" }}>
        {msg.content}
      </span>
    </div>
  );
}

function AssistantBlock({ msg }: { msg: TimestampedMessage }) {
  const isError = msg.content.startsWith("[error]");
  return (
    <div className="flex items-start gap-3 py-0.5">
      <span className="text-xs shrink-0 tabular-nums mt-0.5" style={{ color: "var(--text-muted)" }}>
        {formatTime(msg.ts)}
      </span>
      <span className="text-xs shrink-0 mt-0.5" style={{ color: isError ? "var(--error)" : "var(--accent)" }}>
        jar
      </span>
      <span
        className="text-sm whitespace-pre-wrap leading-relaxed"
        style={{ color: isError ? "var(--error)" : "var(--text)" }}
      >
        {msg.content}
      </span>
    </div>
  );
}

function ThinkingLine() {
  return (
    <div className="flex items-center gap-3 py-0.5">
      <span className="text-xs tabular-nums" style={{ color: "var(--text-muted)" }}>
        {formatTime(new Date())}
      </span>
      <span className="text-xs" style={{ color: "var(--accent)" }}>
        jar
      </span>
      <span className="text-xs" style={{ color: "var(--text-dim)" }}>
        thinking<BlinkCursor />
      </span>
    </div>
  );
}

function BlinkCursor() {
  return (
    <span
      style={{ animation: "blink 1s step-end infinite", color: "var(--accent)" }}
    >
      ▊
    </span>
  );
}
