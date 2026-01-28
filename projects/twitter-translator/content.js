(() => {
  const TRANSLATED_ATTR = "data-shud-translated";
  const BTN_CLASS = "shud-translate-btn";
  const BLOCK_CLASS = "shud-translation-block";

  let enabled = true;
  let autoMode = false;

  // Load settings
  chrome.storage.sync.get({ enabled: true, autoMode: false }, (settings) => {
    enabled = settings.enabled;
    autoMode = settings.autoMode;
    if (enabled) {
      init();
    }
  });

  // Listen for setting changes
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.enabled) {
      enabled = changes.enabled.newValue;
      if (enabled) {
        processTweets();
      } else {
        removeAllButtons();
      }
    }
    if (changes.autoMode) {
      autoMode = changes.autoMode.newValue;
    }
  });

  function init() {
    processTweets();

    const observer = new MutationObserver((mutations) => {
      if (!enabled) return;
      let shouldProcess = false;
      for (const mutation of mutations) {
        if (mutation.addedNodes.length > 0) {
          shouldProcess = true;
          break;
        }
      }
      if (shouldProcess) {
        processTweets();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  function processTweets() {
    const tweetTexts = document.querySelectorAll('[data-testid="tweetText"]');

    tweetTexts.forEach((tweetTextEl) => {
      if (tweetTextEl.getAttribute(TRANSLATED_ATTR)) return;
      tweetTextEl.setAttribute(TRANSLATED_ATTR, "true");

      // Find the parent article
      const article = tweetTextEl.closest('article[data-testid="tweet"]');
      if (!article) return;

      // Create translate button
      const btn = document.createElement("button");
      btn.className = BTN_CLASS;
      btn.textContent = "번역";
      btn.addEventListener("click", () => handleTranslate(btn, tweetTextEl));

      // Insert button after the tweet text
      tweetTextEl.parentNode.insertBefore(btn, tweetTextEl.nextSibling);

      // Auto translate if enabled
      if (autoMode) {
        handleTranslate(btn, tweetTextEl);
      }
    });
  }

  async function handleTranslate(btn, tweetTextEl) {
    const existingBlock = btn.nextElementSibling;
    if (existingBlock && existingBlock.classList.contains(BLOCK_CLASS)) {
      // Toggle visibility
      if (existingBlock.style.display === "none") {
        existingBlock.style.display = "block";
        btn.textContent = "번역 숨기기";
        btn.classList.add("active");
      } else {
        existingBlock.style.display = "none";
        btn.textContent = "번역";
        btn.classList.remove("active");
      }
      return;
    }

    const text = tweetTextEl.innerText.trim();
    if (!text) return;

    btn.textContent = "번역 중...";
    btn.disabled = true;

    try {
      const translated = await translateText(text);

      // If translation is same as original, it's likely already Korean
      if (translated === text) {
        btn.textContent = "이미 한국어";
        btn.disabled = true;
        btn.classList.add("same-lang");
        return;
      }

      const block = document.createElement("div");
      block.className = BLOCK_CLASS;
      block.textContent = translated;

      btn.parentNode.insertBefore(block, btn.nextSibling);

      btn.textContent = "번역 숨기기";
      btn.disabled = false;
      btn.classList.add("active");
    } catch (err) {
      console.error("Translation error:", err);
      btn.textContent = "번역 실패 (재시도)";
      btn.disabled = false;
    }
  }

  async function translateText(text) {
    const url =
      "https://translate.googleapis.com/translate_a/single?" +
      new URLSearchParams({
        client: "gtx",
        sl: "auto",
        tl: "ko",
        dt: "t",
        q: text,
      });

    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();

    // Response format: [[["translated","original",...], ...], ...]
    let translated = "";
    if (data && data[0]) {
      for (const segment of data[0]) {
        if (segment[0]) {
          translated += segment[0];
        }
      }
    }

    return translated;
  }

  function removeAllButtons() {
    document.querySelectorAll(`.${BTN_CLASS}`).forEach((btn) => btn.remove());
    document
      .querySelectorAll(`.${BLOCK_CLASS}`)
      .forEach((block) => block.remove());
    document.querySelectorAll(`[${TRANSLATED_ATTR}]`).forEach((el) => {
      el.removeAttribute(TRANSLATED_ATTR);
    });
  }
})();
