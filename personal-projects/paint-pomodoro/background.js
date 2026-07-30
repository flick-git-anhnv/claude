// Paint Pomodoro — background service worker
// Owns the timer state machine and artwork fetching. Persists everything to
// chrome.storage.local so popup/content scripts can read it directly.

const ALARM_NAME = "paintPomodoroPhaseEnd";
const MET_SEARCH_URL =
  "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q=painting";
const MET_OBJECT_URL = (id) =>
  `https://collectionapi.metmuseum.org/public/collection/v1/objects/${id}`;
const MET_CACHE_TTL_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

const DEFAULT_SETTINGS = {
  workMinutes: 25,
  restMinutes: 5,
  artSource: "met", // 'met' | 'custom' | 'upload'
  customUrls: [],
  uploadedImages: [], // data URLs, capped client-side
};

const DEFAULT_STATE = {
  phase: "idle", // 'idle' | 'work' | 'rest'
  running: false,
  phaseStartAt: null,
  phaseEndAt: null,
  phaseTotalMs: null, // fixed duration of the current phase; phaseEndAt shifts on resume, this doesn't
  remainingMsWhenPaused: null,
  currentTaskId: null,
  artwork: null, // { imageUrl, title, artist, sourceUrl }
  sessionsCompletedToday: 0,
  lastSessionDay: null,
};

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

async function getAll() {
  const data = await chrome.storage.local.get([
    "settings",
    "state",
    "tasks",
    "history",
    "metCache",
  ]);
  return {
    settings: data.settings || DEFAULT_SETTINGS,
    state: data.state || DEFAULT_STATE,
    tasks: data.tasks || [],
    history: data.history || [],
    metCache: data.metCache || null,
  };
}

async function setState(patch) {
  const { state } = await getAll();
  const next = { ...state, ...patch };
  await chrome.storage.local.set({ state: next });
  return next;
}

// Clicking the toolbar icon opens the side panel (docked, stays open across
// tabs) instead of a transient popup that closes on outside click.
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch(() => {});

chrome.runtime.onInstalled.addListener(async () => {
  const data = await chrome.storage.local.get([
    "settings",
    "state",
    "tasks",
    "history",
  ]);
  if (!data.settings) await chrome.storage.local.set({ settings: DEFAULT_SETTINGS });
  if (!data.state) await chrome.storage.local.set({ state: DEFAULT_STATE });
  if (!data.tasks) await chrome.storage.local.set({ tasks: [] });
  if (!data.history) await chrome.storage.local.set({ history: [] });
});

// ---- Artwork fetching -------------------------------------------------

async function refreshMetCache() {
  try {
    const res = await fetch(MET_SEARCH_URL);
    const json = await res.json();
    const ids = Array.isArray(json.objectIDs) ? json.objectIDs.slice(0, 500) : [];
    const cache = { ids, fetchedAt: Date.now(), recentlyShown: [] };
    await chrome.storage.local.set({ metCache: cache });
    return cache;
  } catch (e) {
    return null;
  }
}

async function fetchRandomMetArtwork() {
  let { metCache } = await getAll();
  if (!metCache || !metCache.ids?.length || Date.now() - metCache.fetchedAt > MET_CACHE_TTL_MS) {
    metCache = await refreshMetCache();
  }
  if (!metCache || !metCache.ids?.length) return null;

  const recentlyShown = metCache.recentlyShown || [];
  for (let attempt = 0; attempt < 8; attempt++) {
    const id = metCache.ids[Math.floor(Math.random() * metCache.ids.length)];
    if (recentlyShown.includes(id)) continue;
    try {
      const res = await fetch(MET_OBJECT_URL(id));
      const obj = await res.json();
      const imageUrl = obj.primaryImage || obj.primaryImageSmall;
      if (!imageUrl) continue;
      const updatedRecent = [id, ...recentlyShown].slice(0, 10);
      await chrome.storage.local.set({
        metCache: { ...metCache, recentlyShown: updatedRecent },
      });
      return {
        imageUrl,
        title: obj.title || "Untitled",
        artist: obj.artistDisplayName || "Unknown artist",
        sourceUrl: obj.objectURL || "https://www.metmuseum.org/art/collection",
      };
    } catch (e) {
      continue;
    }
  }
  return null;
}

async function pickArtwork(settings) {
  if (settings.artSource === "custom" && settings.customUrls?.length) {
    const url = settings.customUrls[Math.floor(Math.random() * settings.customUrls.length)];
    return { imageUrl: url, title: "Ảnh tùy chỉnh", artist: "", sourceUrl: null };
  }
  if (settings.artSource === "upload" && settings.uploadedImages?.length) {
    const img =
      settings.uploadedImages[Math.floor(Math.random() * settings.uploadedImages.length)];
    return { imageUrl: img, title: "Ảnh cá nhân", artist: "", sourceUrl: null };
  }
  const met = await fetchRandomMetArtwork();
  if (met) return met;
  // Fallback so the overlay never has nothing to show.
  return {
    imageUrl: null,
    title: "Không tải được tranh — kiểm tra kết nối mạng",
    artist: "",
    sourceUrl: null,
  };
}

// ---- Phase state machine ------------------------------------------------

async function scheduleAlarm(when) {
  await chrome.alarms.clear(ALARM_NAME);
  await chrome.alarms.create(ALARM_NAME, { when });
}

async function startWorkPhase() {
  const { settings } = await getAll();
  const now = Date.now();
  const duration = settings.workMinutes * 60 * 1000;
  const end = now + duration;
  await setState({
    phase: "work",
    running: true,
    phaseStartAt: now,
    phaseEndAt: end,
    phaseTotalMs: duration,
    remainingMsWhenPaused: null,
    artwork: null,
  });
  await scheduleAlarm(end);
}

async function startRestPhase() {
  const { settings } = await getAll();
  const now = Date.now();
  const duration = settings.restMinutes * 60 * 1000;
  const end = now + duration;
  await setState({
    phase: "rest",
    running: true,
    phaseStartAt: now,
    phaseEndAt: end,
    phaseTotalMs: duration,
    remainingMsWhenPaused: null,
  });
  await scheduleAlarm(end);
  // Fetch artwork async and patch it in once ready (don't block phase start).
  const artwork = await pickArtwork(settings);
  await setState({ artwork });
}

async function completeWorkSession() {
  const { state, tasks, history, settings } = await getAll();
  const day = todayKey();
  const sessionsCompletedToday = state.lastSessionDay === day ? state.sessionsCompletedToday + 1 : 1;
  const task = tasks.find((t) => t.id === state.currentTaskId);
  const entry = {
    id: `${Date.now()}`,
    date: day,
    taskId: state.currentTaskId,
    taskText: task ? task.text : null,
    durationMinutes: settings.workMinutes,
    completedAt: Date.now(),
  };
  await chrome.storage.local.set({ history: [entry, ...history].slice(0, 200) });
  await setState({ sessionsCompletedToday, lastSessionDay: day });
}

async function transitionPhase() {
  const { state } = await getAll();
  if (state.phase === "work") {
    await completeWorkSession();
    await startRestPhase();
  } else if (state.phase === "rest") {
    await startWorkPhase();
  }
}

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === ALARM_NAME) transitionPhase();
});

// ---- Message handling from popup/content -------------------------------

async function handleAction(message) {
  const { action, payload } = message;
  const { state, settings, tasks } = await getAll();

  switch (action) {
    case "START": {
      if (state.phase === "idle") {
        if (payload?.taskId) await setState({ currentTaskId: payload.taskId });
        await startWorkPhase();
      } else if (!state.running) {
        // resuming from pause
        const now = Date.now();
        const end = now + (state.remainingMsWhenPaused ?? 0);
        await setState({ running: true, phaseEndAt: end, remainingMsWhenPaused: null });
        await scheduleAlarm(end);
      }
      return { ok: true };
    }
    case "PAUSE": {
      if (state.running && state.phase !== "idle") {
        const remaining = Math.max(0, state.phaseEndAt - Date.now());
        await chrome.alarms.clear(ALARM_NAME);
        await setState({ running: false, remainingMsWhenPaused: remaining });
      }
      return { ok: true };
    }
    case "SKIP": {
      if (state.phase !== "idle") {
        await chrome.alarms.clear(ALARM_NAME);
        await transitionPhase();
      }
      return { ok: true };
    }
    case "RESET": {
      await chrome.alarms.clear(ALARM_NAME);
      await setState(DEFAULT_STATE);
      return { ok: true };
    }
    case "SELECT_TASK": {
      await setState({ currentTaskId: payload.taskId });
      return { ok: true };
    }
    case "ADD_TASK": {
      const newTask = { id: `${Date.now()}`, text: payload.text, done: false, createdAt: Date.now() };
      await chrome.storage.local.set({ tasks: [newTask, ...tasks] });
      return { ok: true, task: newTask };
    }
    case "TOGGLE_TASK": {
      const next = tasks.map((t) => (t.id === payload.taskId ? { ...t, done: !t.done } : t));
      await chrome.storage.local.set({ tasks: next });
      return { ok: true };
    }
    case "DELETE_TASK": {
      const next = tasks.filter((t) => t.id !== payload.taskId);
      await chrome.storage.local.set({ tasks: next });
      if (state.currentTaskId === payload.taskId) await setState({ currentTaskId: null });
      return { ok: true };
    }
    case "UPDATE_SETTINGS": {
      const next = { ...settings, ...payload };
      await chrome.storage.local.set({ settings: next });
      return { ok: true, settings: next };
    }
    default:
      return { ok: false, error: "unknown action" };
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleAction(message).then(sendResponse);
  return true; // keep the message channel open for the async response
});
