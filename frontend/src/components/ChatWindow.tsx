import { useEffect, useRef } from "react";
import type { ChatMessage, TopicSuggestion } from "../types";
import MessageBubble from "./MessageBubble";
import WelcomeScreen from "./WelcomeScreen";

interface ChatWindowProps {
  messages: ChatMessage[];
  isThinking: boolean;
  onSelectTopic: (topic: TopicSuggestion) => void;
}

export default function ChatWindow({ messages, isThinking, onSelectTopic }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, isThinking]);

  if (messages.length === 0) {
    return <WelcomeScreen onSelectTopic={onSelectTopic} />;
  }

  return (
    <div className="mx-auto flex h-full w-full max-w-3xl flex-col gap-5 overflow-y-auto scrollbar-thin px-6 py-6">
      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}

      {isThinking && (
        <div className="flex justify-start">
          <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm border border-parchment-line bg-parchment px-4 py-3.5">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="h-1.5 w-1.5 animate-bounce rounded-full bg-vana-500"
                style={{ animationDelay: `${i * 120}ms` }}
              />
            ))}
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
