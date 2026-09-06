/**
 * Core domain types for the IP-SAKTI Sahayak frontend module.
 * These mirror the shape expected from the RAG backend response contract;
 * adjust field names here if the backend schema differs.
 */

export type LanguageCode = "en" | "hi" | "sa" | "ta" | "te" | "kn" | "ml";

export interface LanguageOption {
  code: LanguageCode;
  label: string;
  nativeLabel: string;
}

/** Broad regime an answer or source belongs to, used for filter chips and badges. */
export type IPRegime =
  | "patents"
  | "trademarks"
  | "geographical-indications"
  | "traditional-knowledge"
  | "international";

export interface RegimeMeta {
  id: IPRegime;
  label: string;
  shortLabel: string;
}

/** A single retrieved source backing part of an assistant answer. */
export interface Source {
  id: string;
  title: string;
  authority: string; // e.g. "Indian Patent Office", "WIPO", "GI Registry, Chennai"
  citation: string; // formal citation string, e.g. "Patents Act 1970, s.3(p)"
  url?: string;
  regime: IPRegime;
  jurisdiction: string; // e.g. "India", "International (WIPO)", "European Union"
  excerpt: string; // short quoted/paraphrased snippet shown in the citation card
  retrievedAt?: string;
}

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  language: LanguageCode;
  content: string;
  /** Indices into `sources` referenced inline in `content` as [1], [2] etc. */
  sources?: Source[];
  regimes?: IPRegime[];
  confidence?: "high" | "medium" | "low";
  createdAt: string;
}

export interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
  messages: ChatMessage[];
}

export interface TopicSuggestion {
  id: string;
  label: string;
  regime: IPRegime;
  prompt: string;
}
