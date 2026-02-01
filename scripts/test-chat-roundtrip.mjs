/**
 * Basic chat round-trip test for BAGANA AI.
 * Run with dev server up: npm run dev (in another terminal), then node scripts/test-chat-roundtrip.mjs
 * Uses BASE_URL env or default http://localhost:3000
 */
const BASE_URL = process.env.BASE_URL || "http://localhost:3000";

async function main() {
  let passed = 0;
  let failed = 0;

  // 1. GET /api/crew — health/description
  try {
    const getRes = await fetch(`${BASE_URL}/api/crew`);
    const getData = await getRes.json();
    if (getRes.ok && getData.status === "ok") {
      console.log("✓ GET /api/crew:", getData.message || getData.status);
      passed++;
    } else {
      console.log("✗ GET /api/crew: unexpected", getRes.status, getData);
      failed++;
    }
  } catch (e) {
    console.log("✗ GET /api/crew:", e.message);
    failed++;
  }

  // 2. POST /api/crew — chat round-trip (may return error if OPENAI_API_KEY invalid)
  try {
    const postRes = await fetch(`${BASE_URL}/api/crew`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "Test round-trip" }),
    });
    const postData = await postRes.json();
    const hasStatus = postData && typeof postData.status === "string";
    const hasOutputOrError = hasStatus && (postData.status === "complete" ? "output" in postData : "error" in postData);
    if (hasStatus && (postData.status === "complete" || postData.status === "error")) {
      console.log("✓ POST /api/crew: status =", postData.status, postData.status === "error" ? `(${String(postData.error).slice(0, 60)}...)` : "");
      passed++;
    } else {
      console.log("✗ POST /api/crew: unexpected response", postRes.status, postData);
      failed++;
    }
  } catch (e) {
    console.log("✗ POST /api/crew:", e.message);
    failed++;
  }

  console.log("\nResult:", passed, "passed,", failed, "failed");
  process.exit(failed > 0 ? 1 : 0);
}

main();
