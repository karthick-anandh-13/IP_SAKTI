/**
 * test-api.js
 * Exercises every IP-SAKTI Sahayak backend endpoint end-to-end using Axios,
 * printing a pass/fail report. Intended as a smoke test, not a replacement
 * for a real test suite (e.g. pytest on the backend side).
 *
 * Usage:
 *   BASE_URL=http://localhost:8080 node test-api.js
 */
import axios from "axios";

const BASE_URL = process.env.BASE_URL || "http://localhost:8080";
const api = axios.create({ baseURL: BASE_URL, validateStatus: () => true });

let passed = 0;
let failed = 0;

function report(name, ok, extra = "") {
  if (ok) {
    passed += 1;
    console.log(`  \u2713 ${name}`);
  } else {
    failed += 1;
    console.log(`  \u2717 ${name} ${extra}`);
  }
}

function assert(condition, name, details) {
  report(name, !!condition, details ? `— ${JSON.stringify(details)}` : "");
}

const runId = Date.now();
const testUser = {
  name: "API Test User",
  email: `api.test.${runId}@example.com`,
  password: "TestPass1234",
};

let token = null;
let sessionId = null;
let documentId = null;

async function testHealth() {
  console.log("\n[Health]");
  const res = await api.get("/health");
  assert(res.status === 200, "GET /health", res.data);
}

async function testAuth() {
  console.log("\n[Auth]");

  const register = await api.post("/auth/register", testUser);
  assert(register.status === 201 && register.data.access_token, "POST /auth/register", register.data);
  token = register.data.access_token;

  const duplicateRegister = await api.post("/auth/register", testUser);
  assert(duplicateRegister.status === 409, "POST /auth/register (duplicate rejected)", duplicateRegister.data);

  const badLogin = await api.post("/auth/login", { email: testUser.email, password: "wrong" });
  assert(badLogin.status === 401, "POST /auth/login (wrong password rejected)", badLogin.data);

  const login = await api.post("/auth/login", {
    email: testUser.email,
    password: testUser.password,
  });
  assert(login.status === 200 && login.data.access_token, "POST /auth/login", login.data);
  token = login.data.access_token;

  const me = await api.get("/auth/me", { headers: authHeader() });
  assert(me.status === 200 && me.data.email === testUser.email, "GET /auth/me", me.data);

  const unauthMe = await api.get("/auth/me");
  assert(unauthMe.status === 401, "GET /auth/me (no token rejected)", unauthMe.data);
}

function authHeader() {
  return { Authorization: `Bearer ${token}` };
}

async function testChatSessions() {
  console.log("\n[Chat Sessions]");

  const create = await api.post(
    "/chat/session",
    { title: "Prior Art Query", language: "en" },
    { headers: authHeader() }
  );
  assert(create.status === 201 && create.data.id, "POST /chat/session", create.data);
  sessionId = create.data.id;

  const list = await api.get("/chat/sessions", { headers: authHeader() });
  assert(
    list.status === 200 && Array.isArray(list.data) && list.data.some((s) => s.id === sessionId),
    "GET /chat/sessions",
    list.data
  );

  const detail = await api.get(`/chat/${sessionId}`, { headers: authHeader() });
  assert(detail.status === 200 && detail.data.id === sessionId, `GET /chat/${sessionId}`, detail.data);

  const userMessage = await api.post(
    `/chat/${sessionId}/message`,
    { sender: "user", message: "What is prior art?" },
    { headers: authHeader() }
  );
  assert(userMessage.status === 201, `POST /chat/${sessionId}/message (user)`, userMessage.data);

  const assistantMessage = await api.post(
    `/chat/${sessionId}/message`,
    {
      sender: "assistant",
      message: "Prior art refers to any evidence that your invention is already known.",
      source_citation: "Patents Act, 1970, Section 2(1)(l)",
    },
    { headers: authHeader() }
  );
  assert(assistantMessage.status === 201, `POST /chat/${sessionId}/message (assistant)`, assistantMessage.data);

  const detailWithMessages = await api.get(`/chat/${sessionId}`, { headers: authHeader() });
  assert(
    detailWithMessages.data.messages && detailWithMessages.data.messages.length === 2,
    `GET /chat/${sessionId} (contains messages)`,
    detailWithMessages.data
  );

  const notFound = await api.get(`/chat/nonexistent-id`, { headers: authHeader() });
  assert(notFound.status === 404, "GET /chat/{id} (unknown id -> 404)", notFound.data);
}

async function testAskGateway() {
  console.log("\n[AI Gateway]");
  // This will typically fail with 502/504 unless a RAG service is actually
  // running at RAG_SERVICE_URL — that's expected in an isolated test run.
  const ask = await api.post(
    "/ask",
    { question: "What is prior art?", language: "en", session_id: sessionId },
    { headers: authHeader() }
  );
  const acceptable = [200, 502, 504].includes(ask.status);
  assert(
    acceptable,
    "POST /ask (reaches gateway logic)",
    { status: ask.status, note: "502/504 expected if no RAG service is running locally" }
  );
}

async function testDocuments() {
  console.log("\n[Documents]");

  const create = await api.post(
    "/documents",
    {
      title: "Test Regulation Document",
      jurisdiction: "India",
      category: "Patent Law",
      language: "en",
      source_url: "https://example.com/doc",
    },
    { headers: authHeader() }
  );
  assert(create.status === 201 && create.data.id, "POST /documents", create.data);
  documentId = create.data.id;

  const list = await api.get("/documents");
  assert(
    list.status === 200 && list.data.some((d) => d.id === documentId),
    "GET /documents",
    list.data
  );

  const filtered = await api.get("/documents?jurisdiction=India&category=Patent Law");
  assert(filtered.status === 200, "GET /documents (filtered)", filtered.data);

  const detail = await api.get(`/documents/${documentId}`);
  assert(detail.status === 200 && detail.data.id === documentId, `GET /documents/${documentId}`, detail.data);

  const unauthCreate = await api.post("/documents", {
    title: "Should Fail",
    jurisdiction: "India",
    category: "Patent Law",
  });
  assert(unauthCreate.status === 401, "POST /documents (no token rejected)", unauthCreate.data);
}

async function testFeedback() {
  console.log("\n[Feedback]");

  const create = await api.post("/feedback", {
    session_id: sessionId,
    rating: 5,
    comment: "Very helpful and accurate citation.",
  });
  assert(create.status === 201 && create.data.id, "POST /feedback", create.data);

  const list = await api.get(`/feedback?session_id=${sessionId}`);
  assert(list.status === 200 && list.data.length >= 1, "GET /feedback", list.data);
}

async function testCleanup() {
  console.log("\n[Cleanup]");

  const deleteDoc = await api.delete(`/documents/${documentId}`, { headers: authHeader() });
  assert(deleteDoc.status === 204, `DELETE /documents/${documentId}`, deleteDoc.data);

  const deleteSession = await api.delete(`/chat/${sessionId}`, { headers: authHeader() });
  assert(deleteSession.status === 204, `DELETE /chat/${sessionId}`, deleteSession.data);

  const confirmGone = await api.get(`/chat/${sessionId}`, { headers: authHeader() });
  assert(confirmGone.status === 404, `GET /chat/${sessionId} (confirms deletion)`, confirmGone.data);
}

async function main() {
  console.log(`Running IP-SAKTI Sahayak API test suite against ${BASE_URL}`);

  await testHealth();
  await testAuth();
  await testChatSessions();
  await testAskGateway();
  await testDocuments();
  await testFeedback();
  await testCleanup();

  console.log(`\n${"=".repeat(50)}`);
  console.log(`Results: ${passed} passed, ${failed} failed`);
  console.log("=".repeat(50));

  process.exit(failed > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error("Test run crashed:", err);
  process.exit(1);
});
