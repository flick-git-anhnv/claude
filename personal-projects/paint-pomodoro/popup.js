const MAX_UPLOADED_IMAGES = 10;

function send(action, payload) {
  return chrome.runtime.sendMessage({ action, payload });
}

function formatMs(ms) {
  const total = Math.max(0, Math.ceil(ms / 1000));
  const m = Math.floor(total / 60)
    .toString()
    .padStart(2, "0");
  const s = (total % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// ---- Tabs ----------------------------------------------------------------

document.querySelectorAll(".pp-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".pp-tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".pp-panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.querySelector(`.pp-panel[data-panel="${tab.dataset.tab}"]`).classList.add("active");
  });
});

// ---- Timer panel -----------------------------------------------------------

const phaseLabelEl = document.getElementById("phaseLabel");
const clockEl = document.getElementById("clock");
const currentTaskEl = document.getElementById("currentTask");
const todayCountEl = document.getElementById("todayCount");
const btnStart = document.getElementById("btnStart");
const btnPause = document.getElementById("btnPause");
const btnSkip = document.getElementById("btnSkip");
const btnReset = document.getElementById("btnReset");

let tickHandle = null;
let latestState = null;
let latestTasks = [];

const PHASE_LABELS = { idle: "Sẵn sàng", work: "Đang tập trung", rest: "Đang nghỉ" };

function renderTimer() {
  if (!latestState) return;
  const { phase, running, phaseEndAt, remainingMsWhenPaused, currentTaskId } = latestState;
  phaseLabelEl.textContent = PHASE_LABELS[phase] || phase;

  const remaining = running ? phaseEndAt - Date.now() : remainingMsWhenPaused ?? 0;
  clockEl.textContent = phase === "idle" ? formatMinutes() : formatMs(remaining);

  const task = latestTasks.find((t) => t.id === currentTaskId);
  currentTaskEl.textContent = task ? `Task: ${task.text}` : "Không có task được chọn";
  todayCountEl.textContent = latestState.sessionsCompletedToday || 0;

  btnStart.hidden = running;
  btnStart.textContent = phase === "idle" ? "Bắt đầu" : "Tiếp tục";
  btnPause.hidden = !running;
  btnSkip.hidden = phase === "idle";

  renderPip();
}

function formatMinutes() {
  // Shown only while idle, before the first phase starts.
  return "--:--";
}

function startTickLoop() {
  if (tickHandle) return;
  tickHandle = setInterval(() => {
    if (latestState?.running) renderTimer();
  }, 500);
}

btnStart.addEventListener("click", async () => {
  await send("START", { taskId: latestState?.currentTaskId || null });
  await refreshAll();
});
btnPause.addEventListener("click", async () => {
  await send("PAUSE");
  await refreshAll();
});
btnSkip.addEventListener("click", async () => {
  await send("SKIP");
  await refreshAll();
});
btnReset.addEventListener("click", async () => {
  await send("RESET");
  await refreshAll();
});

// ---- Pin to desktop (Document Picture-in-Picture) --------------------------
// Opens a real always-on-top OS window (floats above every app, not just
// Chrome) showing a mini timer. Requires Chrome 116+.

const btnPip = document.getElementById("btnPip");
let pipWindow = null;
let pipEls = null;

function buildPipDocument(win) {
  const style = win.document.createElement("style");
  style.textContent = `
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #14141a;
      color: #f4f1ea;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
    }
    .pip-app { text-align: center; padding: 10px; }
    .pip-phase {
      font-size: 11px;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      opacity: 0.65;
      margin-bottom: 4px;
    }
    .pip-clock {
      font-size: 44px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      color: #e03d2e;
      line-height: 1;
      margin-bottom: 10px;
    }
    .pip-controls { display: flex; gap: 6px; justify-content: center; }
    button {
      border: 1px solid rgba(244, 241, 234, 0.25);
      background: rgba(244, 241, 234, 0.06);
      color: #f4f1ea;
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 12px;
      cursor: pointer;
    }
    button:hover { background: rgba(244, 241, 234, 0.14); }
  `;
  win.document.head.appendChild(style);
  win.document.body.innerHTML = `
    <div class="pip-app">
      <div class="pip-phase" id="pipPhase">Sẵn sàng</div>
      <div class="pip-clock" id="pipClock">--:--</div>
      <div class="pip-controls">
        <button id="pipStart">Bắt đầu</button>
        <button id="pipPause" hidden>Tạm dừng</button>
        <button id="pipSkip" hidden>Bỏ qua</button>
      </div>
    </div>
  `;
  const els = {
    phase: win.document.getElementById("pipPhase"),
    clock: win.document.getElementById("pipClock"),
    start: win.document.getElementById("pipStart"),
    pause: win.document.getElementById("pipPause"),
    skip: win.document.getElementById("pipSkip"),
  };
  els.start.addEventListener("click", async () => {
    await send("START", { taskId: latestState?.currentTaskId || null });
    await refreshAll();
  });
  els.pause.addEventListener("click", async () => {
    await send("PAUSE");
    await refreshAll();
  });
  els.skip.addEventListener("click", async () => {
    await send("SKIP");
    await refreshAll();
  });
  return els;
}

function renderPip() {
  if (!pipWindow || !pipEls || !latestState) return;
  const { phase, running, phaseEndAt, remainingMsWhenPaused } = latestState;
  pipEls.phase.textContent = PHASE_LABELS[phase] || phase;
  const remaining = running ? phaseEndAt - Date.now() : remainingMsWhenPaused ?? 0;
  pipEls.clock.textContent = phase === "idle" ? "--:--" : formatMs(remaining);
  pipEls.start.hidden = running;
  pipEls.start.textContent = phase === "idle" ? "Bắt đầu" : "Tiếp tục";
  pipEls.pause.hidden = !running;
  pipEls.skip.hidden = phase === "idle";
}

btnPip.addEventListener("click", async () => {
  if (!("documentPictureInPicture" in window)) {
    alert(
      "Trình duyệt này chưa hỗ trợ Pin ra màn hình (cần Chrome/Edge 116 trở lên)."
    );
    return;
  }
  if (pipWindow) {
    pipWindow.focus();
    return;
  }
  pipWindow = await documentPictureInPicture.requestWindow({ width: 220, height: 170 });
  pipEls = buildPipDocument(pipWindow);
  renderPip();
  pipWindow.addEventListener("pagehide", () => {
    pipWindow = null;
    pipEls = null;
  });
});

// ---- Tasks panel -----------------------------------------------------------

const taskForm = document.getElementById("taskForm");
const taskInput = document.getElementById("taskInput");
const taskListEl = document.getElementById("taskList");

taskForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = taskInput.value.trim();
  if (!text) return;
  await send("ADD_TASK", { text });
  taskInput.value = "";
  await refreshAll();
});

function renderTasks() {
  taskListEl.innerHTML = "";
  latestTasks.forEach((task) => {
    const li = document.createElement("li");
    if (task.done) li.classList.add("done");

    const textSpan = document.createElement("span");
    textSpan.className = "pp-task-text";
    textSpan.textContent = task.text;
    textSpan.addEventListener("click", async () => {
      await send("TOGGLE_TASK", { taskId: task.id });
      await refreshAll();
    });

    const selectBtn = document.createElement("button");
    selectBtn.className = "pp-task-select";
    if (latestState?.currentTaskId === task.id) selectBtn.classList.add("selected");
    selectBtn.textContent = "Chọn";
    selectBtn.addEventListener("click", async () => {
      await send("SELECT_TASK", { taskId: task.id });
      await refreshAll();
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "pp-task-delete";
    deleteBtn.textContent = "✕";
    deleteBtn.addEventListener("click", async () => {
      await send("DELETE_TASK", { taskId: task.id });
      await refreshAll();
    });

    li.append(textSpan, selectBtn, deleteBtn);
    taskListEl.appendChild(li);
  });
}

// ---- History panel ---------------------------------------------------------

const historySummaryEl = document.getElementById("historySummary");
const historyListEl = document.getElementById("historyList");

function renderHistory(history) {
  if (!history.length) {
    historySummaryEl.textContent = "Chưa có phiên nào hoàn thành.";
    historyListEl.innerHTML = "";
    return;
  }
  const totalMinutes = history.reduce((sum, h) => sum + (h.durationMinutes || 0), 0);
  historySummaryEl.textContent = `${history.length} phiên hoàn thành · ${totalMinutes} phút tập trung tổng cộng`;
  historyListEl.innerHTML = "";
  history.slice(0, 30).forEach((entry) => {
    const li = document.createElement("li");
    const date = new Date(entry.completedAt).toLocaleString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "2-digit",
    });
    li.innerHTML = `<span class="pp-hist-date">${date}</span>${entry.taskText || "(không có task)"} · ${entry.durationMinutes}p`;
    historyListEl.appendChild(li);
  });
}

// ---- Settings panel ---------------------------------------------------------

const workMinutesInput = document.getElementById("workMinutes");
const restMinutesInput = document.getElementById("restMinutes");
const artSourceSelect = document.getElementById("artSource");
const customUrlsField = document.getElementById("customUrlsField");
const customUrlsInput = document.getElementById("customUrls");
const uploadField = document.getElementById("uploadField");
const uploadInput = document.getElementById("uploadInput");
const uploadPreview = document.getElementById("uploadPreview");
const btnSaveSettings = document.getElementById("btnSaveSettings");

let pendingUploadedImages = [];

function toggleArtSourceFields() {
  const val = artSourceSelect.value;
  customUrlsField.hidden = val !== "custom";
  uploadField.hidden = val !== "upload";
}

artSourceSelect.addEventListener("change", toggleArtSourceFields);

uploadInput.addEventListener("change", async () => {
  const files = Array.from(uploadInput.files || []);
  const dataUrls = await Promise.all(files.map(fileToDataUrl));
  pendingUploadedImages = [...pendingUploadedImages, ...dataUrls].slice(0, MAX_UPLOADED_IMAGES);
  renderUploadPreview();
});

function renderUploadPreview() {
  uploadPreview.innerHTML = "";
  pendingUploadedImages.forEach((src) => {
    const img = document.createElement("img");
    img.src = src;
    uploadPreview.appendChild(img);
  });
}

function renderSettings(settings) {
  workMinutesInput.value = settings.workMinutes;
  restMinutesInput.value = settings.restMinutes;
  artSourceSelect.value = settings.artSource;
  customUrlsInput.value = (settings.customUrls || []).join("\n");
  pendingUploadedImages = settings.uploadedImages || [];
  renderUploadPreview();
  toggleArtSourceFields();
}

btnSaveSettings.addEventListener("click", async () => {
  const customUrls = customUrlsInput.value
    .split("\n")
    .map((s) => s.trim())
    .filter(Boolean);
  await send("UPDATE_SETTINGS", {
    workMinutes: Math.max(1, parseInt(workMinutesInput.value, 10) || 25),
    restMinutes: Math.max(1, parseInt(restMinutesInput.value, 10) || 5),
    artSource: artSourceSelect.value,
    customUrls,
    uploadedImages: pendingUploadedImages,
  });
  btnSaveSettings.textContent = "Đã lưu ✓";
  setTimeout(() => (btnSaveSettings.textContent = "Lưu cài đặt"), 1200);
});

// ---- Refresh / sync ---------------------------------------------------------

async function refreshAll() {
  const data = await chrome.storage.local.get(["state", "tasks", "history", "settings"]);
  latestState = data.state;
  latestTasks = data.tasks || [];
  renderTimer();
  renderTasks();
  renderHistory(data.history || []);
  renderSettings(data.settings || {});
}

chrome.storage.onChanged.addListener((changes, area) => {
  if (area !== "local") return;
  refreshAll();
});

startTickLoop();
refreshAll();
