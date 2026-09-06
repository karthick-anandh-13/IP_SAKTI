import { useLanguage } from "../context/LanguageContext";
import { REGIMES, TOPIC_SUGGESTIONS } from "../data/mockData";
import type { TopicSuggestion } from "../types";
import RegimeBadge from "./RegimeBadge";

export default function WelcomeScreen({
  onSelectTopic,
}: {
  onSelectTopic: (topic: TopicSuggestion) => void;
}) {
  const { t } = useLanguage();

  return (
    <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center px-6 text-center">
      <h2 className="font-display text-2xl font-medium text-vana-900">
        {t("welcomeHeading")}
      </h2>
      <p className="mt-3 text-sm leading-relaxed text-ink-soft">{t("welcomeBody")}</p>

      <div className="mt-6 flex flex-wrap justify-center gap-2">
        {REGIMES.map((r) => (
          <RegimeBadge key={r.id} regime={r.id} />
        ))}
      </div>

      <div className="mt-8 grid w-full gap-2 sm:grid-cols-2">
        {TOPIC_SUGGESTIONS.map((topic) => (
          <button
            key={topic.id}
            onClick={() => onSelectTopic(topic)}
            className="rounded-lg border border-parchment-line bg-parchment px-4 py-3 text-left text-sm
                       text-ink-soft transition-colors hover:border-vana-300 hover:text-ink
                       focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vana-600"
          >
            {topic.label}
          </button>
        ))}
      </div>
    </div>
  );
}
