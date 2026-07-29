// Paint Pomodoro — content script
// Renders a full-viewport overlay during REST phases that slowly reveals a
// painting as the break progresses. Reads state directly from
// chrome.storage.local so it works even if injected mid-break (e.g. after a
// page navigation).

(() => {
  let overlayEl = null;
  let imgEl = null;
  let timerEl = null;
  let artworkEl = null;
  let rafId = null;
  let lastPhase = null;
  let lastArtworkUrl = null;

  function formatMs(ms) {
    const total = Math.max(0, Math.ceil(ms / 1000));
    const m = Math.floor(total / 60)
      .toString()
      .padStart(2, "0");
    const s = (total % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  }

  function ensureOverlay() {
    if (overlayEl) return overlayEl;
    overlayEl = document.createElement("div");
    overlayEl.id = "paint-pomodoro-overlay";
    overlayEl.innerHTML = `
      <img class="pp-image" alt="" />
      <div class="pp-card">
        <div class="pp-eyebrow">Rest break — painting</div>
        <div class="pp-timer">05:00</div>
        <div class="pp-artwork"></div>
        <button class="pp-skip" type="button">Skip break</button>
      </div>
    `;
    document.documentElement.appendChild(overlayEl);
    imgEl = overlayEl.querySelector(".pp-image");
    timerEl = overlayEl.querySelector(".pp-timer");
    artworkEl = overlayEl.querySelector(".pp-artwork");
    overlayEl.querySelector(".pp-skip").addEventListener("click", () => {
      chrome.runtime.sendMessage({ action: "SKIP" });
    });
    return overlayEl;
  }

  function renderArtwork(artwork) {
    if (!artwork || !artwork.imageUrl) {
      artworkEl.textContent = artwork?.title || "Đang tải tranh...";
      imgEl.removeAttribute("src");
      return;
    }
    if (lastArtworkUrl !== artwork.imageUrl) {
      imgEl.src = artwork.imageUrl;
      lastArtworkUrl = artwork.imageUrl;
    }
    const caption = artwork.artist ? `${artwork.title} — ${artwork.artist}` : artwork.title;
    if (artwork.sourceUrl) {
      artworkEl.innerHTML = `${caption} · <a href="${artwork.sourceUrl}" target="_blank" rel="noopener">The Met</a>`;
    } else {
      artworkEl.textContent = caption;
    }
  }

  function tick(state) {
    if (!state.running || state.phase !== "rest") {
      stopLoop();
      return;
    }
    const now = Date.now();
    const total = state.phaseTotalMs || state.phaseEndAt - state.phaseStartAt;
    const remaining = state.phaseEndAt - now;
    const elapsed = total - remaining;
    const fraction = total > 0 ? Math.min(1, Math.max(0, elapsed / total)) : 0;
    // Ease-out growth so the reveal feels gradual, not linear.
    const radius = Math.pow(fraction, 0.7) * 150; // 150% comfortably covers viewport corners
    imgEl.style.clipPath = `circle(${radius.toFixed(2)}% at 50% 50%)`;
    timerEl.textContent = formatMs(remaining);
    rafId = requestAnimationFrame(() => tick(state));
  }

  function stopLoop() {
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
  }

  function showOverlay(state) {
    ensureOverlay();
    renderArtwork(state.artwork);
    overlayEl.classList.add("visible");
    stopLoop();
    tick(state);
  }

  function hideOverlay() {
    stopLoop();
    if (overlayEl) overlayEl.classList.remove("visible");
  }

  async function refreshFromStorage() {
    const { state } = await chrome.storage.local.get(["state"]);
    if (!state) return;
    const isRestActive = state.phase === "rest" && state.running;
    if (isRestActive) {
      showOverlay(state);
    } else if (lastPhase === "rest") {
      hideOverlay();
    }
    lastPhase = state.phase;
  }

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area !== "local" || !changes.state) return;
    const state = changes.state.newValue;
    if (!state) return;
    const isRestActive = state.phase === "rest" && state.running;
    if (isRestActive) {
      showOverlay(state);
    } else {
      hideOverlay();
    }
    lastPhase = state.phase;
  });

  refreshFromStorage();
})();
