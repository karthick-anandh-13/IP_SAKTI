import type { IPRegime } from "../types";
import { REGIMES } from "../data/mockData";

const REGIME_STYLES: Record<IPRegime, string> = {
  patents: "bg-vana-50 text-vana-700 border-vana-100",
  trademarks: "bg-haldi-100 text-haldi-700 border-haldi-300",
  "geographical-indications": "bg-vana-50 text-vana-700 border-vana-100",
  "traditional-knowledge": "bg-kumkum-500/10 text-kumkum-600 border-kumkum-500/20",
  international: "bg-parchment-dim text-ink-soft border-parchment-line",
};

export default function RegimeBadge({ regime }: { regime: IPRegime }) {
  const meta = REGIMES.find((r) => r.id === regime);
  if (!meta) return null;

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${REGIME_STYLES[regime]}`}
    >
      {meta.shortLabel}
    </span>
  );
}
