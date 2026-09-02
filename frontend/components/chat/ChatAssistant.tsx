"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Sparkles,
  X,
  Send,
  Trash2,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { streamChatMessage, fetchChatStatus, ChatMessageHistoryItem } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  grounded?: boolean;
  isConfigured?: boolean;
  timestamp: string;
}

const STARTER_QUESTIONS = [
  "Which assets are idle right now?",
  "Why is EQX1002 flagged?",
  "What's our avoided cost so far?",
  "How do I check out equipment?",
  "How does the anomaly score work?",
  "Which equipment is currently unassigned?",
];

export function ChatAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null);
  const [modelName, setModelName] = useState("gemini-2.5-flash");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Check backend Gemini status on mount
  useEffect(() => {
    fetchChatStatus()
      .then((status) => {
        setIsConfigured(status.is_configured);
        if (status.model) setModelName(status.model);
      })
      .catch(() => setIsConfigured(false));
  }, []);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, isLoading]);

  // Focus input on open
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  const msgCounterRef = useRef(0);

  const [streamingStage, setStreamingStage] = useState<string | null>(null);

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputMessage).trim();
    if (!query || isLoading) return;

    msgCounterRef.current += 1;
    const currentMsgId = `user-msg-${msgCounterRef.current}`;
    const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    const userMessage: Message = {
      id: currentMsgId,
      role: "user",
      content: query,
      timestamp: timeStr,
    };

    // Append user message immediately
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInputMessage("");
    setIsLoading(true);
    setStreamingStage("Consulting live fleet telemetry...");

    // Build history payload (last 6 turns)
    const historyPayload: ChatMessageHistoryItem[] = updatedMessages
      .slice(-6)
      .map((m) => ({
        role: m.role === "assistant" ? "model" : "user",
        content: m.content,
      }));

    msgCounterRef.current += 1;
    const assistantMsgId = `assistant-msg-${msgCounterRef.current}`;
    let accumulatedText = "";

    await streamChatMessage(query, historyPayload, {
      onStage: (stageText) => {
        setStreamingStage(stageText);
      },
      onChunk: (chunkText) => {
        accumulatedText += chunkText;
        setStreamingStage(null);
        setMessages((prev) => {
          const existingIdx = prev.findIndex((m) => m.id === assistantMsgId);
          if (existingIdx >= 0) {
            const copy = [...prev];
            copy[existingIdx] = {
              ...copy[existingIdx],
              content: accumulatedText,
            };
            return copy;
          } else {
            return [
              ...prev,
              {
                id: assistantMsgId,
                role: "assistant",
                content: accumulatedText,
                grounded: true,
                isConfigured: true,
                timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
              },
            ];
          }
        });
      },
      onDone: (meta) => {
        setIsLoading(false);
        setStreamingStage(null);
        if (meta.is_configured !== undefined) {
          setIsConfigured(meta.is_configured);
        }
      },
      onError: (errMsg) => {
        setIsLoading(false);
        setStreamingStage(null);
        setMessages((prev) => {
          const existingIdx = prev.findIndex((m) => m.id === assistantMsgId);
          const errorMsgObj: Message = {
            id: assistantMsgId,
            role: "assistant",
            content: errMsg,
            grounded: false,
            isConfigured: isConfigured ?? false,
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          };
          if (existingIdx >= 0) {
            const copy = [...prev];
            copy[existingIdx] = errorMsgObj;
            return copy;
          }
          return [...prev, errorMsgObj];
        });
      },
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  // Simple Markdown text renderer for bolding, bullet points, headers, and code
  const renderFormattedText = (text: string) => {
    return text.split("\n").map((line, idx) => {
      // Check for header
      if (line.startsWith("### ")) {
        return (
          <h4 key={idx} className="font-semibold text-xs tracking-wider uppercase text-[#111111] mt-2.5 mb-1">
            {line.replace("### ", "")}
          </h4>
        );
      }
      if (line.startsWith("## ") || line.startsWith("# ")) {
        return (
          <h3 key={idx} className="font-semibold text-sm text-[#111111] mt-3 mb-1">
            {line.replace(/^[#]+\s*/, "")}
          </h3>
        );
      }

      // Check for bullet line
      const isBullet = line.trim().startsWith("- ") || line.trim().startsWith("* ");
      const content = isBullet ? line.trim().replace(/^[-*]\s*/, "") : line;

      // Parse bold **text**
      const parts = content.split(/(\*\*.*?\*\*)/g);

      const parsedContent = parts.map((part, pIdx) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          const boldText = part.slice(2, -2);
          // Highlight equipment ID with soft orange tint
          const isEqId = /^EQX[0-9A-Z-]+$/i.test(boldText);
          return (
            <strong
              key={pIdx}
              className={cn(
                "font-semibold text-[#111111]",
                isEqId && "bg-[#ff5a24]/10 text-[#e04d1a] px-1 py-0.5 rounded font-mono text-[11px]"
              )}
            >
              {boldText}
            </strong>
          );
        }
        return part;
      });

      if (isBullet) {
        return (
          <li key={idx} className="ml-3.5 list-disc my-0.5 leading-relaxed">
            {parsedContent}
          </li>
        );
      }

      if (!line.trim()) {
        return <div key={idx} className="h-1.5" />;
      }

      return (
        <p key={idx} className="my-0.5 leading-relaxed">
          {parsedContent}
        </p>
      );
    });
  };

  return (
    <>
      {/* Floating Launch Button */}
      {!isOpen && (
        <button
          id="rentsense-chat-launcher"
          onClick={() => setIsOpen(true)}
          className={cn(
            "fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-full",
            "bg-[#111111] text-white shadow-[0_12px_36px_rgba(0,0,0,0.25)] border border-white/15",
            "hover:bg-black hover:scale-[1.03] active:scale-[0.98] transition-all duration-200 group"
          )}
          aria-label="Open RentSense AI Copilot"
        >
          <div className="relative flex items-center justify-center">
            <Sparkles className="size-4 text-[#ff5a24] transition-transform group-hover:rotate-12" />
            <span className="absolute -top-1 -right-1 flex size-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#ff5a24] opacity-75"></span>
              <span className="relative inline-flex rounded-full size-2 bg-[#ff5a24]"></span>
            </span>
          </div>
          <span className="text-xs font-semibold tracking-wide">RentSense Copilot</span>
          <span className="text-[10px] uppercase font-bold tracking-widest bg-white/10 px-1.5 py-0.5 rounded text-white/70">
            AI
          </span>
        </button>
      )}

      {/* Floating Chat Modal Panel */}
      {isOpen && (
        <div
          id="rentsense-chat-panel"
          className={cn(
            "fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50",
            "w-[calc(100vw-2rem)] sm:w-[430px] h-[600px] max-h-[86vh]",
            "flex flex-col rounded-2xl bg-[#fbfbfa]/95 backdrop-blur-2xl",
            "border border-black/15 shadow-[0_24px_64px_rgba(0,0,0,0.24)] overflow-hidden",
            "animate-in fade-in slide-in-from-bottom-4 duration-200"
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3.5 bg-[#111111] text-white border-b border-white/10 select-none">
            <div className="flex items-center gap-2.5">
              <div className="size-3 bg-[#ff5a24] rounded-sm flex-shrink-0" />
              <div>
                <div className="flex items-center gap-1.5">
                  <h3
                    className="text-sm font-medium tracking-tight text-white leading-none"
                    style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
                  >
                    RentSense Copilot
                  </h3>
                  <span className="text-[9px] uppercase font-bold tracking-wider px-1 py-0.5 rounded bg-white/10 text-white/70">
                    Gemini
                  </span>
                </div>
                <div className="flex items-center gap-1.5 mt-1">
                  <span
                    className={cn(
                      "size-1.5 rounded-full",
                      isConfigured === true
                        ? "bg-emerald-400 animate-pulse"
                        : isConfigured === false
                        ? "bg-amber-400"
                        : "bg-white/40"
                    )}
                  />
                  <span className="text-[10px] text-white/60 tracking-wider">
                    {isConfigured === true
                      ? "Grounded Live Fleet Data"
                      : isConfigured === false
                      ? "Unconfigured (Offline)"
                      : "Connecting..."}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              {messages.length > 0 && (
                <button
                  onClick={clearChat}
                  title="Clear conversation"
                  className="p-1.5 text-white/60 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
                >
                  <Trash2 className="size-3.5" />
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                title="Close Copilot"
                className="p-1.5 text-white/60 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
              >
                <X className="size-4" />
              </button>
            </div>
          </div>

          {/* Unconfigured Warning Banner */}
          {isConfigured === false && (
            <div className="bg-amber-500/10 border-b border-amber-500/20 px-3.5 py-2 flex items-start gap-2 text-[11px] text-amber-900">
              <AlertCircle className="size-3.5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <span className="font-semibold">Gemini API Key Required:</span> Configure{" "}
                <code className="bg-amber-500/15 px-1 rounded font-mono text-[10px]">GEMINI_API_KEY</code> in{" "}
                <code className="bg-amber-500/15 px-1 rounded font-mono text-[10px]">.env</code> to activate live
                intelligence.
              </div>
            </div>
          )}

          {/* Message Thread Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs text-[#252525]">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col justify-between py-2">
                {/* Intro Hero */}
                <div className="text-center pt-4 px-2">
                  <div className="size-10 bg-black text-white rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-md">
                    <Sparkles className="size-5 text-[#ff5a24]" />
                  </div>
                  <h4
                    className="text-base font-semibold text-black tracking-tight"
                    style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
                  >
                    Fleet Intelligence Assistant
                  </h4>
                  <p className="text-[11px] text-[#6a6a6a] mt-1 max-w-xs mx-auto leading-relaxed">
                    Ask real-time questions about active equipment, idle machines, anomaly scores, or RentSense workflows.
                  </p>
                </div>

                {/* Starter Question Chips */}
                <div className="space-y-1.5 pt-4">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-[#7a7a7a] px-1">
                    Suggested Inquiries
                  </p>
                  <div className="grid grid-cols-1 gap-1.5">
                    {STARTER_QUESTIONS.map((q, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(q)}
                        className="text-left px-3 py-2 rounded-xl bg-white border border-black/10 hover:border-[#ff5a24]/50 hover:bg-[#ff5a24]/5 transition-all text-[11px] text-[#252525] flex items-center justify-between group shadow-2xs"
                      >
                        <span className="truncate">{q}</span>
                        <ArrowRight className="size-3 text-[#999] group-hover:text-[#ff5a24] transition-colors flex-shrink-0 ml-1" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={cn("flex flex-col", msg.role === "user" ? "items-end" : "items-start")}
                >
                  {/* Sender Name & Timestamp */}
                  <div className="flex items-center gap-1.5 mb-1 px-1">
                    <span className="text-[10px] font-semibold text-[#888]">
                      {msg.role === "user" ? "You" : "RentSense Copilot"}
                    </span>
                    <span className="text-[9px] text-[#aaa]">{msg.timestamp}</span>
                    {msg.role === "assistant" && msg.grounded && (
                      <span className="inline-flex items-center gap-0.5 text-[9px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1 rounded font-medium">
                        <ShieldCheck className="size-2.5" /> Grounded
                      </span>
                    )}
                  </div>

                  {/* Bubble */}
                  <div
                    className={cn(
                      "max-w-[88%] px-3.5 py-2.5 rounded-2xl text-[12px]",
                      msg.role === "user"
                        ? "bg-[#111111] text-white rounded-tr-xs shadow-sm"
                        : "bg-white/90 text-[#1a1a1a] rounded-tl-xs border border-black/10 shadow-xs"
                    )}
                  >
                    {msg.role === "user" ? (
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <div className="space-y-0.5">{renderFormattedText(msg.content)}</div>
                    )}
                  </div>
                </div>
              ))
            )}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex flex-col items-start">
                <div className="flex items-center gap-1.5 mb-1 px-1">
                  <span className="text-[10px] font-semibold text-[#888]">RentSense Copilot</span>
                  <span className="text-[9px] text-[#aaa]">Analyzing fleet state...</span>
                </div>
                <div className="px-3.5 py-2.5 rounded-2xl rounded-tl-xs bg-white/90 border border-black/10 shadow-xs flex items-center gap-1.5">
                  <div className="size-1.5 bg-[#ff5a24] rounded-full animate-bounce" />
                  <div className="size-1.5 bg-[#ff5a24] rounded-full animate-bounce [animation-delay:0.2s]" />
                  <div className="size-1.5 bg-[#ff5a24] rounded-full animate-bounce [animation-delay:0.4s]" />
                  <span className="text-[11px] text-[#777] ml-1.5">{streamingStage || "Synthesizing fleet answer..."}</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Footer */}
          <div className="p-3 bg-white border-t border-black/10">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2"
            >
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  isConfigured === false
                    ? "Enter question (Gemini unconfigured)..."
                    : "Ask about idle assets, alerts, or workflows..."
                }
                disabled={isLoading}
                className="flex-1 bg-[#f6f5f2] border border-black/10 focus:border-[#ff5a24] focus:bg-white rounded-xl px-3.5 py-2 text-xs text-black placeholder:text-[#888] focus:outline-hidden transition-all disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className={cn(
                  "p-2.5 rounded-xl bg-[#111111] text-white transition-all shadow-xs flex-shrink-0",
                  "hover:bg-[#ff5a24] active:scale-95 disabled:opacity-40 disabled:hover:bg-[#111111] disabled:cursor-not-allowed"
                )}
                aria-label="Send message"
              >
                <Send className="size-3.5" />
              </button>
            </form>
            <div className="flex items-center justify-between mt-1.5 px-1 text-[9px] text-[#888]">
              <span>Read-only AI copilot · Grounded in live backend state</span>
              <span className="font-mono">{modelName}</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
