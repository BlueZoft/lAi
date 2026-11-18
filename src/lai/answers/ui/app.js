"use strict";
(() => {
  const form = document.getElementById("scenario-form"),
    input = document.getElementById("scenario"),
    language = document.getElementById("display-language"),
    queryLanguage = document.getElementById("query-language"),
    submit = document.getElementById("submit"),
    results = document.getElementById("results"),
    availability = document.getElementById("availability");
  let capabilities = null,
    labels = null,
    controller = null,
    epoch = 0,
    idleTimer = null;
  const index = () => (language.value === "en" ? 1 : 0);
  const t = (key) => labels?.[key]?.[index()] || key;
  const node = (tag, text, cls) => {
    const n = document.createElement(tag);
    if (text !== undefined) n.textContent = String(text);
    if (cls) n.className = cls;
    return n;
  };
  function link(url) {
    try {
      const u = new URL(url);
      if (!["https:", "http:"].includes(u.protocol) || u.username || u.password)
        throw new Error();
      const a = node("a", url);
      a.href = u.href;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      return a;
    } catch {
      return node("span", url);
    }
  }
  function refresh() {
    document.documentElement.lang = language.value;
    if (labels)
      document.querySelectorAll("[data-copy]").forEach((n) => {
        n.textContent = t(n.dataset.copy);
      });
    input.lang = queryLanguage.value === "si-Latn" ? "si" : queryLanguage.value;
    const ready = Boolean(
      labels &&
        capabilities?.private_navigation_configured &&
        capabilities?.copy_reviewed?.[language.value],
    );
    input.disabled = queryLanguage.disabled = submit.disabled = !ready;
    availability.hidden = ready;
  }
  function clear() {
    if (idleTimer) window.clearTimeout(idleTimer);
    idleTimer = null;
    epoch++;
    if (controller) controller.abort();
    controller = null;
    input.value = "";
    results.replaceChildren();
    refresh();
  }
  function touch() {
    if (idleTimer) window.clearTimeout(idleTimer);
    idleTimer = window.setTimeout(clear, 300000);
  }
  input.addEventListener("input", touch);
  window.addEventListener("pagehide", clear);
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) clear();
  });
  function render(data) {
    results.replaceChildren(node("h2", t(data.status)));
    for (const message of data.messages || [])
      results.append(node("p", message));
    for (const p of data.provisions || []) {
      const candidate = p.candidate,
        citation = candidate.citation,
        card = node("article", undefined, "provision");
      card.append(
        node(
          "h3",
          `${citation.instrument_type} ${citation.number} · ${citation.year} · ${citation.section}`,
        ),
        node("p", `${t("sourceLanguage")}: ${citation.language}`, "caption"),
      );
      const quote = node("blockquote", candidate.text, "quote");
      quote.lang = citation.language;
      card.append(quote);
      if (p.gloss)
        card.append(
          node("h3", t("reviewed")),
          node("p", p.gloss.text, "gloss"),
        );
      else card.append(node("p", t("missing"), "warning"));
      card.append(node("p", t("currency"), "warning"));
      const details = node("details");
      details.append(node("summary", t("provenance")));
      const dl = node("dl");
      for (const [key, names] of Object.entries(labels.citation)) {
        const value = citation[key];
        dl.append(node("dt", names[index()]));
        const dd = node("dd");
        if ((key === "source_url" || key === "canonical_url") && value)
          dd.append(link(value));
        else
          dd.textContent = Array.isArray(value)
            ? value.join(", ")
            : String(value ?? "—");
        dl.append(dd);
      }
      details.append(dl);
      card.append(details);
      results.append(card);
    }
    if ((data.referrals || []).length) {
      results.append(
        node("h2", t("referrals")),
        node("p", t("listing"), "caption"),
      );
      for (const referral of data.referrals) {
        const card = node("article", undefined, "referral");
        card.append(
          node("h3", referral.organisation),
          node("p", referral.service_description),
        );
        const dl = node("dl");
        for (const [key, value] of [
          [
            "phone",
            [referral.phone, ...referral.additional_phones]
              .filter(Boolean)
              .join(" / "),
          ],
          ["address", referral.address],
          ["channel", referral.channel],
          ["checked", referral.verified_on],
          ["due", referral.review_due],
        ])
          if (value) dl.append(node("dt", t(key)), node("dd", value));
        dl.append(node("dt", labels.citation.source_url[index()]));
        const dd = node("dd");
        dd.append(link(referral.source_url));
        dl.append(dd);
        card.append(dl);
        results.append(card);
      }
    }
    if ((data.warnings || []).includes("referral_unavailable"))
      results.append(node("p", t("noReferral"), "notice"));
    if ((data.warnings || []).some((w) => w !== "referral_unavailable"))
      results.append(node("p", t("warning"), "caption"));
  }
  document.getElementById("clear").addEventListener("click", clear);
  language.addEventListener("change", clear);
  queryLanguage.addEventListener("change", () => {
    clear();
    input.focus();
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (submit.disabled) return;
    if (controller) controller.abort();
    controller = new AbortController();
    const generation = ++epoch;
    submit.disabled = true;
    results.replaceChildren(node("p", t("busy")));
    try {
      const reply = await fetch("/api/answers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario: { text: input.value, language: queryLanguage.value },
          display_language: language.value,
        }),
        signal: controller.signal,
        cache: "no-store",
        credentials: "omit",
        referrerPolicy: "no-referrer",
      });
      const data = await reply.json();
      if (generation !== epoch) return;
      if (!reply.ok) throw new Error();
      render(data);
      touch();
    } catch (error) {
      if (generation === epoch && error.name !== "AbortError")
        results.replaceChildren(node("p", t("error"), "notice"));
    } finally {
      if (generation === epoch) refresh();
    }
  });
  Promise.all([
    fetch("/api/capabilities", { cache: "no-store", credentials: "omit" }).then(
      (r) => {
        if (!r.ok) throw new Error();
        return r.json();
      },
    ),
    fetch("/assets/labels.json", {
      cache: "no-store",
      credentials: "omit",
    }).then((r) => {
      if (!r.ok) throw new Error();
      return r.json();
    }),
  ])
    .then(([caps, copy]) => {
      capabilities = caps;
      labels = copy;
      refresh();
    })
    .catch(() => {
      availability.hidden = false;
      refresh();
    });
  refresh();
})();
