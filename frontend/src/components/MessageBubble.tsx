import type { ChatMessage } from "../types";
import { useLanguage } from "../context/LanguageContext";
import SourceCitation from "./SourceCitation";

const CONFIDENCE_STYLE: Record<NonNullable<ChatMessage["confidence"]>, string> = {
  high: "bg-vana-50 text-vana-700",
  medium: "bg-haldi-100 text-haldi-700",
  low: "bg-kumkum-500/10 text-kumkum-600",
};

export default function MessageBubble({ message }: { message: ChatMessage }) {
  const { t } = useLanguage();
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-xl rounded-2xl rounded-tr-sm bg-vana-700 px-4 py-3 text-parchment">
          <p className="text-sm leading-relaxed">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-2xl">
        <div className="rounded-2xl rounded-tl-sm border border-parchment-line bg-parchment px-4 py-3.5">
          {message.confidence && (
            <span
              className={`mb-2 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${CONFIDENCE_STYLE[message.confidence]}`}
            >
              {t(
                message.confidence === "high"
                  ? "confidenceHigh"
                  : message.confidence === "medium"
                  ? "confidenceMedium"
                  : "confidenceLow"
              )}
            </span>
          )}
          <p className="whitespace-pre-line text-[0.95rem] leading-relaxed text-ink">
            {message.content}
          </p>
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 space-y-2">
            <h3 className="px-1 text-xs font-medium uppercase tracking-wide text-ink-faint">
              {t("sourcesUsed")}
            </h3>
            {message.sources.map((source, i) => (
              <SourceCitation key={source.id} index={i + 1} source={source} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
