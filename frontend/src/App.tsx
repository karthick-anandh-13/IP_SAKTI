import { useState } from "react";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import QueryInput from "./components/QueryInput";
import NoveltyScanner from "./components/NoveltyScanner";
import { SAMPLE_CONVERSATION } from "./data/mockData";
import type { ChatMessage, Conversation, TopicSuggestion } from "./types";
import { useLanguage } from "./context/LanguageContext";

/**
 * `askBackend` is the single integration point for the RAG backend.
 * Replace this with a real call to the IP-SAKTI Sahayak query API, e.g.:
 *
 *   const res = await fetch("/api/query", {
 *     method: "POST",
 *     headers: { "Content-Type": "application/json" },
 *     body: JSON.stringify({ question, language }),
 *   });
 *   return (await res.json()) as ChatMessage;
 *
 * The mock below only echoes back the sample conversation's answer so the
 * UI is fully demonstrable without a live backend.
 */
async function askBackend(question: string, language: ChatMessage["language"]): Promise<ChatMessage> {
  await new Promise((resolve) => setTimeout(resolve, 900));
  const sample = SAMPLE_CONVERSATION.messages[1];
  return {
    ...sample,
    id: crypto.randomUUID(),
    language,
    content:
      question.trim().length > 0
        ? sample.content
        : "Please enter a question about patents, trademarks, GI, or traditional-knowledge protection.",
    createdAt: new Date().toISOString(),
  };
}

export default function App() {
  const { language } = useLanguage();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [isThinking, setIsThinking] = useState(false);

  const activeConversation = conversations.find((c) => c.id === activeId) ?? null;
  const messages = activeConversation?.messages ?? [];

  function ensureActiveConversation(firstMessage: ChatMessage): Conversation {
    if (activeConversation) return activeConversation;
    const created: Conversation = {
      id: crypto.randomUUID(),
      title: firstMessage.content.slice(0, 60),
      updatedAt: new Date().toISOString(),
      messages: [],
    };
    setConversations((prev) => [created, ...prev]);
    setActiveId(created.id);
    return created;
  }

  function appendMessage(conversationId: string, message: ChatMessage) {
    setConversations((prev) =>
      prev.map((c) =>
        c.id === conversationId
          ? { ...c, messages: [...c.messages, message], updatedAt: new Date().toISOString() }
          : c
      )
    );
  }

  async function handleSubmit(text: string) {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      language,
      content: text,
      createdAt: new Date().toISOString(),
    };

    const conversation = ensureActiveConversation(userMessage);
    appendMessage(conversation.id, userMessage);

    setIsThinking(true);
    const reply = await askBackend(text, language);
    setIsThinking(false);
    appendMessage(conversation.id, reply);
  }

  function handleNewConsultation() {
    setActiveId(null);
  }

  function handleSelectTopic(topic: TopicSuggestion) {
    handleSubmit(topic.prompt);
  }

  return (
    <div className="flex h-screen flex-col bg-parchment">
      <Header />
      <div className="flex min-h-0 flex-1">
        <Sidebar
          conversations={conversations}
          activeConversationId={activeId}
          onSelectConversation={setActiveId}
          onNewConsultation={handleNewConsultation}
          onSelectTopic={handleSelectTopic}
        />
        <main className="flex min-h-0 flex-1 flex-col">
          <NoveltyScanner />
          <div className="min-h-0 flex-1">
            <ChatWindow messages={messages} isThinking={isThinking} onSelectTopic={handleSelectTopic} />
          </div>
          <QueryInput onSubmit={handleSubmit} disabled={isThinking} />
        </main>
      </div>
    </div>
  );
}
