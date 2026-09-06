import { useLanguage } from "../context/LanguageContext";
import { TOPIC_SUGGESTIONS } from "../data/mockData";
import type { Conversation, TopicSuggestion } from "../types";
import RegimeBadge from "./RegimeBadge";

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConsultation: () => void;
  onSelectTopic: (topic: TopicSuggestion) => void;
}

export default function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConsultation,
  onSelectTopic,
}: SidebarProps) {
  const { t } = useLanguage();

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-parchment-line bg-parchment-dim">
      <div className="p-4">
        <button
          onClick={onNewConsultation}
          className="w-full rounded-lg bg-vana-700 px-4 py-2.5 text-sm font-medium text-parchment
                     transition-colors hover:bg-vana-900 focus-visible:outline-none focus-visible:ring-2
                     focus-visible:ring-vana-600 focus-visible:ring-offset-2 focus-visible:ring-offset-parchment-dim"
        >
          {t("newConsultation")}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin px-4 pb-4">
        <section className="mb-6">
          <h2 className="mb-2 text-xs font-medium uppercase tracking-wide text-ink-faint">
            {t("topics")}
          </h2>
          <ul className="space-y-1.5">
            {TOPIC_SUGGESTIONS.map((topic) => (
              <li key={topic.id}>
                <button
                  onClick={() => onSelectTopic(topic)}
                  className="group flex w-full flex-col items-start gap-1 rounded-md px-2.5 py-2 text-left
                             hover:bg-parchment focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vana-600"
                >
                  <span className="text-sm leading-snug text-ink-soft group-hover:text-ink">
                    {topic.label}
                  </span>
                  <RegimeBadge regime={topic.regime} />
                </button>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h2 className="mb-2 text-xs font-medium uppercase tracking-wide text-ink-faint">
            {t("history")}
          </h2>
          {conversations.length === 0 ? (
            <p className="px-2.5 text-sm text-ink-faint">—</p>
          ) : (
            <ul className="space-y-1">
              {conversations.map((c) => (
                <li key={c.id}>
                  <button
                    onClick={() => onSelectConversation(c.id)}
                    className={`w-full truncate rounded-md px-2.5 py-2 text-left text-sm transition-colors
                      ${
                        c.id === activeConversationId
                          ? "bg-vana-100 text-vana-900"
                          : "text-ink-soft hover:bg-parchment"
                      }`}
                  >
                    {c.title}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </aside>
  );
}
