# IP-SAKTI Sahayak — Frontend & UX Module

Frontend module for **IP-SAKTI Sahayak**, a multilingual, RAG-based AI assistant for
Intellectual Property and regulatory guidance in Ayurveda. Built with **React 18,
TypeScript, and Tailwind CSS**.

This module implements the consultation (chat) interface: a question box, a
source-cited answer view, an IP-regime taxonomy (patents / trademarks / GI /
traditional knowledge / international regimes), a multilingual UI layer, and a
history + suggested-topics sidebar. It is wired to a mock backend function so it
runs and is fully demonstrable standalone; swap in the real RAG API at the one
integration point noted below.

## Getting started

Requires Node.js 18+.

```bash
npm install
npm run dev       # start local dev server (Vite) at http://localhost:5173
npm run build     # type-check and produce a production build in dist/
npm run preview   # preview the production build locally
```

## Project structure

```
src/
  App.tsx                    # top-level layout & state (conversations, active thread)
  main.tsx                   # React root, wraps App in LanguageProvider
  index.css                  # Tailwind layers + base styles
  types/index.ts             # shared domain types (ChatMessage, Source, IPRegime, ...)
  context/LanguageContext.tsx# current UI language + t() translation helper
  data/
    translations.ts          # UI string translations (en, hi — extend per language)
    mockData.ts               # sample languages, regimes, topic suggestions, demo thread
  components/
    Header.tsx                # app title, tagline, language selector
    LanguageSelector.tsx       # language <select>, backed by LanguageContext
    Sidebar.tsx                # new consultation, suggested topics, past consultations
    ChatWindow.tsx             # scrollable message list / welcome state / typing indicator
    WelcomeScreen.tsx          # empty-state screen with topic shortcuts
    MessageBubble.tsx          # single user/assistant turn, incl. confidence badge
    SourceCitation.tsx         # expandable citation card (authority, excerpt, link)
    RegimeBadge.tsx            # small pill tagging a message/source's IP regime
    QueryInput.tsx             # composer textarea + send button + disclaimer
```

## Design language

The visual system is deliberately drawn from the subject matter rather than a
generic SaaS template:

- **Parchment surface** (`#F5F1E6`) evokes a manuscript page — the register the
  content (statutes, registry entries, classical texts) actually belongs to.
- **Vana** (Sanskrit: "forest") green is the primary action color, drawn from
  neem/tulsi rather than a generic corporate blue.
- **Haldi** (turmeric) marks citations and highlights; **Kumkum** (vermillion)
  is reserved for low-confidence/alert states only.
- **Fraunces** (a warm display serif) is used for headings to nod at the
  manuscript tradition; **Inter** carries body and UI text for legal legibility.
  **Noto Sans Devanagari** is loaded for correct rendering of Hindi/Sanskrit.

All tokens live in `tailwind.config.js` — change them there, not per-component.

## Backend integration point

All calls to the RAG backend are isolated in one function, `askBackend` in
`src/App.tsx`. Replace its body with a real request to your query API:

```ts
async function askBackend(question: string, language: LanguageCode): Promise<ChatMessage> {
  const res = await fetch("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, language }),
  });
  return (await res.json()) as ChatMessage;
}
```

The expected response shape is `ChatMessage` (see `src/types/index.ts`): message
text, a `sources[]` array (title, authority, citation string, jurisdiction,
regime, excerpt, optional URL), an overall `confidence`, and the `regimes[]`
the answer touches. Keep this contract in sync with whatever your RAG/backend
team ships.

## Extending languages

1. Add the language to `LANGUAGES` in `src/data/mockData.ts`.
2. Add a matching translation block in `src/data/translations.ts` (falls back
   to English for any missing key via `t()`).
3. If the script needs a dedicated typeface, add it to `index.html`'s Google
   Fonts link and to `fontFamily` in `tailwind.config.js`.

## Notes for the wider team

- This module owns UI/UX only — no state persistence, auth, or real network
  calls are wired in. `Conversation` state currently lives in React state in
  `App.tsx`; swap for a store (Zustand/Redux) or server-persisted history once
  the backend contract is finalized.
- Citation rendering assumes each source can supply a short excerpt and a
  formal citation string; if the retrieval layer can also return exact
  page/section anchors, `Source.url` can be extended to a deep link.
- Accessibility: interactive elements use visible focus rings and
  `aria-expanded` on the citation toggle; verify against WCAG 2.1 AA as content
  is finalized, especially color contrast once real brand colors are locked in.
