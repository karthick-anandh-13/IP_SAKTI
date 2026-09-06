import { useLanguage } from "../context/LanguageContext";
import LanguageSelector from "./LanguageSelector";

export default function Header() {
  const { t } = useLanguage();

  return (
    <header className="flex items-center justify-between border-b border-parchment-line px-6 py-4">
      <div className="flex items-baseline gap-3">
        <h1 className="font-display text-xl font-medium tracking-tight text-vana-900">
          {t("appName")}
        </h1>
        <p className="hidden text-sm text-ink-faint sm:block">{t("tagline")}</p>
      </div>
      <LanguageSelector />
    </header>
  );
}
