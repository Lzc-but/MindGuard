const SESSION_KEY = "mental_guard_chat_session_id";

function randomId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function getOrCreateSessionId(): string {
  const current = localStorage.getItem(SESSION_KEY);
  if (current) return current;
  const next = randomId();
  localStorage.setItem(SESSION_KEY, next);
  return next;
}
