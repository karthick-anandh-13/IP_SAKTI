import { useState } from "react";
import { scanNovelty, type NoveltyScanResponse } from "../services/noveltyApi";

export default function NoveltyScanner() {
  const [invention, setInvention] = useState("");
  const [result, setResult] = useState<NoveltyScanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleScan() {
    if (invention.trim().length < 10) {
      setError("Please describe the invention in at least 10 characters.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await scanNovelty({
        invention: invention.trim(),
        top_k: 5,
      });

      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to complete novelty scan."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-6">
      <div className="rounded-2xl border border-parchment-line bg-parchment p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-ink">
          Novelty / Prior-Art Risk Scanner
        </h2>

        <p className="mt-2 text-sm text-ink-muted">
          Describe your invention or formulation to search the available
          prior-art records.
        </p>

        <textarea
          value={invention}
          onChange={(e) => setInvention(e.target.value)}
          placeholder="Example: A herbal wound-healing formulation containing turmeric (Curcuma longa) powder for topical application to wounds."
          className="mt-4 min-h-32 w-full rounded-xl border border-parchment-line bg-white p-3 text-sm outline-none focus:ring-2 focus:ring-vana-500"
        />

        <button
          type="button"
          onClick={handleScan}
          disabled={loading}
          className="mt-4 rounded-xl bg-vana-600 px-5 py-2.5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Scanning..." : "Scan for Prior Art"}
        </button>

        {error && (
          <p className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </p>
        )}

        {result && (
          <div className="mt-6 space-y-4">
            <div>
              <p className="text-sm text-ink-muted">Risk level</p>
              <p className="text-2xl font-bold">{result.risk_level}</p>
            </div>

            <div>
              <p className="text-sm text-ink-muted">Risk score</p>
              <p className="text-lg font-semibold">
                {result.risk_score.toFixed(4)}
              </p>
            </div>

            <div className="rounded-xl bg-white p-4">
              <p className="text-sm font-medium">Summary</p>
              <p className="mt-1 text-sm text-ink-muted">{result.summary}</p>
            </div>

            <div>
              <p className="text-sm font-medium">Potential prior-art matches</p>

              <div className="mt-3 space-y-3">
                {result.matches.map((match) => (
                  <div
                    key={match.doc_id}
                    className="rounded-xl border border-parchment-line bg-white p-4"
                  >
                    <p className="font-medium">{match.title}</p>

                    <p className="mt-1 text-xs text-ink-muted">
                      {match.source_type} · {match.jurisdiction} · similarity{" "}
                      {match.similarity.toFixed(4)}
                    </p>

                    {match.clause_or_section && (
                      <p className="mt-2 text-xs">
                        Section: {match.clause_or_section}
                      </p>
                    )}

                    <p className="mt-2 text-sm text-ink-muted">
                      {match.snippet}
                    </p>

                    {match.official_url && (
                      <a
                        href={match.official_url}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-2 inline-block text-sm underline"
                      >
                        View official source
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <p className="text-xs text-ink-muted">
              This is an AI-generated prior-art risk indicator and does not
              constitute a legal determination of patentability.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
