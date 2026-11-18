/* Optional local browser QA. Run against a loopback app; response mocks are synthetic. */
const { chromium } = require("playwright");
const fs = require("node:fs");
const assert = require("node:assert/strict");
const base = process.argv[2] || "http://127.0.0.1:8015";
const fixture = JSON.parse(
  fs.readFileSync("tests/fixtures/synthetic-answer.json", "utf8"),
);
assert(["127.0.0.1", "localhost"].includes(new URL(base).hostname));

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || "/usr/bin/chromium",
    headless: true,
  });
  try {
    const context = await browser.newContext({
      viewport: { width: 1200, height: 950 },
    });
    const page = await context.newPage();
    const errors = [],
      outbound = [];
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("request", (request) => {
      if (new URL(request.url()).origin !== new URL(base).origin)
        outbound.push(request.url());
    });
    await page.goto(base, { waitUntil: "networkidle" });
    assert(await page.locator("#submit").isDisabled());
    assert.equal(await page.locator("html").getAttribute("lang"), "si");
    await page.screenshot({ path: "/tmp/lai-t5-closed.png" });
    await page.selectOption("#display-language", "en");
    assert(
      (await page.locator("#availability").innerText()).includes("review"),
    );
    assert(await page.locator("#submit").isDisabled());

    await page.route("**/api/capabilities", (route) =>
      route.fulfill({
        json: {
          public_launch_enabled: false,
          private_navigation_configured: true,
          copy_reviewed: { en: true, si: true },
        },
      }),
    );
    let hostile = false,
      received = [],
      slow = false;
    await page.route("**/api/answers", async (route) => {
      const payload = route.request().postDataJSON();
      received.push(payload);
      const result = structuredClone(fixture);
      result.language = payload.display_language;
      if (result.language === "si")
        for (const provision of result.provisions) {
          provision.gloss = null;
          provision.explanation_status = "text_and_referral";
        }
      if (hostile)
        result.provisions[0].candidate.text =
          '<script>window.__injected=true</script><img src="https://example.invalid/leak" onerror="window.__injected=true"> SYNTHETIC hostile source';
      if (slow) await new Promise((resolve) => setTimeout(resolve, 300));
      try {
        await route.fulfill({ json: result });
      } catch {
        /* Clear may have aborted the request. */
      }
    });
    await page.reload({ waitUntil: "networkidle" });
    await page.selectOption("#display-language", "en");
    await page.selectOption("#query-language", "en");
    await page.fill("#scenario", "SYNTHETIC documents catalogue");
    await page.click("#submit");
    await page.locator(".provision").first().waitFor();
    assert.equal(
      await page.locator(".provision").count(),
      fixture.provisions.length,
    );
    assert.equal(
      await page.locator(".quote").first().textContent(),
      fixture.provisions[0].candidate.text,
    );
    assert.equal(await page.locator(".gloss").count(), 1);
    assert.equal(received[0].scenario.language, "en");
    await page
      .locator("details")
      .first()
      .evaluate((node) => {
        node.open = true;
      });
    assert.equal(
      await page.locator("details").first().locator("dt").count(),
      Object.keys(fixture.provisions[0].candidate.citation).length,
    );
    await page.screenshot({
      path: "/tmp/lai-t5-candidates.png",
      fullPage: true,
    });

    hostile = true;
    await page.click("#clear");
    await page.fill("#scenario", "SYNTHETIC documents");
    await page.click("#submit");
    await page.locator(".quote").first().waitFor();
    assert(
      (await page.locator(".quote").first().textContent()).includes("<script>"),
    );
    assert.equal(
      await page.locator("#results img, #results script").count(),
      0,
    );
    assert.equal(await page.evaluate(() => window.__injected), undefined);
    assert.deepEqual(outbound, []);

    await page.click("#clear");
    assert.equal(await page.inputValue("#scenario"), "");
    assert.equal(await page.locator("#results").innerText(), "");
    slow = true;
    await page.fill("#scenario", "SYNTHETIC delayed documents");
    await page.click("#submit");
    await page.click("#clear");
    await page.waitForTimeout(400);
    assert.equal(await page.locator("#results").innerText(), "");
    assert.deepEqual(
      await page.evaluate(() => [localStorage.length, sessionStorage.length]),
      [0, 0],
    );
    assert.equal((await context.cookies()).length, 0);

    await page.setViewportSize({ width: 390, height: 844 });
    await page.selectOption("#display-language", "si");
    hostile = false;
    slow = false;
    await page.fill("#scenario", "SYNTHETIC documents catalogue");
    await page.click("#submit");
    await page.locator(".quote").first().waitFor();
    await page
      .locator("details")
      .first()
      .evaluate((node) => {
        node.open = true;
      });
    assert.equal(await page.locator(".gloss").count(), 0);
    assert.equal(
      await page.locator(".quote").first().textContent(),
      fixture.provisions[0].candidate.text,
    );
    assert.equal(await page.locator("html").getAttribute("lang"), "si");
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    await page.screenshot({ path: "/tmp/lai-t5-mobile.png", fullPage: true });
    assert.deepEqual(errors, []);
    console.log(
      JSON.stringify({
        default_closed: true,
        synthetic_candidates: fixture.provisions.length,
        verbatim_dom: true,
        full_citation: true,
        xss_blocked: true,
        clear_aborts: true,
        storage_empty: true,
        mobile_no_overflow: true,
        page_errors: errors.length,
        external_page_requests: outbound.length,
      }),
    );
    await context.close();
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
