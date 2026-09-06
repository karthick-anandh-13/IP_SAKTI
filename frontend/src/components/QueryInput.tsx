import { useState } from "react";
import type { KeyboardEvent } from "react";
import { useLanguage } from "../context/LanguageContext";

interface QueryInputProps {
  onSubmit: (text: string) => void;
  disabled?: boolean;
}

export default function QueryInput({ onSubmit, disabled }: QueryInputProps) {
  const { t } = useLanguage();
  const [value, setValue] = useState("");

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setValue("");
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="border-t border-parchment-line bg-parchment px-6 py-4">
      <div className="mx-auto flex max-w-3xl items-end gap-3">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t("askPlaceholder")}
          rows={1}
          className="max-h-40 flex-1 resize-none rounded-xl border border-parchment-line bg-white/60 px-4 py-3
                     text-sm text-ink placeholder:text-ink-faint focus-visible:outline-none
                     focus-visible:ring-2 focus-visible:ring-vana-600"
        />
        <button
          onClick={submit}
          disabled={disabled || !value.trim()}
          className="shrink-0 rounded-xl bg-vana-700 px-5 py-3 text-sm font-medium text-parchment
                     transition-colors hover:bg-vana-900 disabled:cursor-not-allowed disabled:bg-ink-faint/40
                     focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vana-600 focus-visible:ring-offset-2"
        >
          {t("send")}
        </button>
      </div>
      <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-ink-faint">
        {t("disclaimer")}
      </p>
    </div>
  );
}
