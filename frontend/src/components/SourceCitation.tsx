import { useState } from "react";
import type { Source } from "../types";
import RegimeBadge from "./RegimeBadge";

interface SourceCitationProps {
  index: number;
  source: Source;
}

export default function SourceCitation({ index, source }: SourceCitationProps) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-lg border border-parchment-line bg-parchment">
      <button
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-start gap-3 px-3 py-2.5 text-left focus-visible:outline-none
                   focus-visible:ring-2 focus-visible:ring-vana-600 rounded-lg"
      >
        <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-haldi-100 text-xs font-medium text-haldi-700">
          {index}
        </span>
        <span className="flex-1">
          <span className="block text-sm font-medium text-ink">{source.title}</span>
          <span className="block text-xs text-ink-faint">
            {source.authority} · {source.jurisdiction}
          </span>
        </span>
        <RegimeBadge regime={source.regime} />
      </button>

      {open && (
        <div className="border-t border-parchment-line px-3 py-3 pl-11 text-sm">
          <p className="mb-2 text-ink-soft">&ldquo;{source.excerpt}&rdquo;</p>
          <p className="mb-2 font-mono text-xs text-ink-faint">{source.citation}</p>
          {source.url && (
            <a
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="text-sm font-medium text-vana-700 underline decoration-vana-300 underline-offset-2 hover:text-vana-900"
            >
              Open source
            </a>
          )}
        </div>
      )}
    </div>
  );
}
