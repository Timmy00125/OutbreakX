const fallbackBase = "http://localhost:8000";

const rawBase =
  process.env.REACT_APP_API_BASE_URL ??
  process.env.REACT_APP_BACKEND_URL ??
  fallbackBase;

export const API_BASE_URL: string = rawBase.replace(/\/+$/, "");

export const CHAT_ENDPOINT = `${API_BASE_URL}/chat`;
