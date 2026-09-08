export interface NoveltyScanRequest {
  invention: string;
  top_k?: number;
}

export interface PriorArtMatch {
  doc_id: string;
  title: string;
  source_type: string;
  jurisdiction: string;
  similarity: number;
  clause_or_section?: string;
  official_url?: string;
  snippet: string;
}

export interface NoveltyScanResponse {
  invention: string;
  risk_level: string;
  risk_score: number;
  summary: string;
  matches: PriorArtMatch[];
}

const BACKEND_URL = "http://127.0.0.1:8000";

export async function scanNovelty(
  request: NoveltyScanRequest
): Promise<NoveltyScanResponse> {
  const response = await fetch(`${BACKEND_URL}/novelty/scan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Novelty scan failed");
  }

  return response.json() as Promise<NoveltyScanResponse>;
}