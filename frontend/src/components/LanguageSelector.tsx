import { useLanguage } from "../context/LanguageContext";
import { LANGUAGES } from "../data/mockData";
import type { LanguageCode } from "../types";

export default function LanguageSelector() {
  const { language, setLanguage } = useLanguage();

  return (
    <label className="relative flex items-center text-sm text-ink-soft">
      <span className="sr-only">Interface language</span>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value as LanguageCode)}
        className="appearance-none rounded-full border border-parchment-line bg-parchment-dim px-3 py-1.5
                   pr-8 text-sm text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-vana-600"
      >
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code}>
            {l.nativeLabel}
          </option>
        ))}
      </select>
      <svg
        aria-hidden="true"
        viewBox="0 0 20 20"
        className="pointer-events-none absolute right-2.5 h-3.5 w-3.5 text-ink-soft"
      >
        <path
          d="M5.5 7.5l4.5 4.5 4.5-4.5"
          stroke="currentColor"
          strokeWidth="1.4"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </label>
  );
}
