/**
 * seed.js
 * Seeds the IP-SAKTI Sahayak backend with sample users and legal/regulatory
 * document metadata.
 *
 * Goes through the public HTTP API (not a direct DB connection) so that
 * password hashing, validation, and business rules stay consistent with
 * whatever the backend enforces.
 *
 * Usage:
 *   BASE_URL=http://localhost:8080 node seed.js
 */
import axios from "axios";

const BASE_URL = process.env.BASE_URL || "http://localhost:8080";

const api = axios.create({ baseURL: BASE_URL, validateStatus: () => true });

const SAMPLE_USERS = [
  { name: "Ananya Rao", email: "ananya.rao@example.com", password: "SecurePass123" },
  { name: "Karthick Anandh", email: "karthick.demo@example.com", password: "SecurePass123" },
  { name: "Dr. Meera Nair", email: "meera.nair@example.com", password: "SecurePass123" },
];

const SAMPLE_DOCUMENTS = [
  {
    title: "The Patents Act, 1970 (as amended)",
    jurisdiction: "India",
    category: "Patent Law",
    language: "en",
    source_url: "https://ipindia.gov.in/patents.htm",
  },
  {
    title: "AYUSH Ministry Guidelines for Ayurveda Drug Licensing",
    jurisdiction: "India",
    category: "Ayurveda Regulatory",
    language: "en",
    source_url: "https://ayush.gov.in/",
  },
  {
    title: "Traditional Knowledge Digital Library (TKDL) Overview",
    jurisdiction: "India",
    category: "Traditional Knowledge / Prior Art",
    language: "en",
    source_url: "https://www.tkdl.res.in/",
  },
  {
    title: "WIPO Patent Cooperation Treaty (PCT) Applicant's Guide",
    jurisdiction: "International",
    category: "Patent Law",
    language: "en",
    source_url: "https://www.wipo.int/pct/en/appguide/",
  },
  {
    title: "Drugs and Cosmetics Act, 1940 — Ayurvedic, Siddha and Unani Drugs",
    jurisdiction: "India",
    category: "Ayurveda Regulatory",
    language: "en",
    source_url: "https://cdsco.gov.in/",
  },
  {
    title: "\u0b95\u0bbe\u0baa\u0bcd\u0baa\u0bc1 \u0bb0\u0bbf\u0b95\u0bbe\u0bb0\u0bcd\u0b9f\u0bcd (Patent Guide - Tamil)",
    jurisdiction: "India",
    category: "Patent Law",
    language: "ta",
    source_url: "https://ipindia.gov.in/patents.htm",
  },
];

async function registerUser(user) {
  const res = await api.post("/auth/register", user);
  if (res.status === 201) {
    console.log(`  [created] user: ${user.email}`);
    return res.data.access_token;
  }
  if (res.status === 409) {
    console.log(`  [exists]  user: ${user.email} — logging in instead`);
    const loginRes = await api.post("/auth/login", {
      email: user.email,
      password: user.password,
    });
    if (loginRes.status === 200) return loginRes.data.access_token;
    console.error(`  [error]   could not log in as ${user.email}:`, loginRes.data);
    return null;
  }
  console.error(`  [error]   could not create ${user.email}:`, res.status, res.data);
  return null;
}

async function createDocument(token, doc) {
  const res = await api.post("/documents", doc, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 201) {
    console.log(`  [created] document: ${doc.title}`);
  } else {
    console.error(`  [error]   could not create document "${doc.title}":`, res.status, res.data);
  }
}

async function main() {
  console.log(`Seeding IP-SAKTI Sahayak backend at ${BASE_URL}\n`);

  console.log("Creating sample users...");
  let firstToken = null;
  for (const user of SAMPLE_USERS) {
    const token = await registerUser(user);
    if (!firstToken && token) firstToken = token;
  }

  if (!firstToken) {
    console.error("\nNo authenticated user available — cannot seed documents. Aborting.");
    process.exit(1);
  }

  console.log("\nCreating sample legal/regulatory documents...");
  for (const doc of SAMPLE_DOCUMENTS) {
    await createDocument(firstToken, doc);
  }

  console.log("\nSeeding complete.");
}

main().catch((err) => {
  console.error("Seed script failed:", err);
  process.exit(1);
});
