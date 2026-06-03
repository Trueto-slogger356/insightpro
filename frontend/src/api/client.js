const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export function getToken() {
  return localStorage.getItem("insightpro_token");
}

export function setToken(token) {
  localStorage.setItem("insightpro_token", token);
}

export function clearToken() {
  localStorage.removeItem("insightpro_token");
}

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((item) => item.msg || JSON.stringify(item)).join("; ")
      : payload.detail;
    throw new Error(detail || "Request failed");
  }

  if (options.raw) {
    return response;
  }
  return response.json();
}

export const api = {
  login: (payload) => request("/api/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  summary: () => request("/api/dashboard/summary"),
  analytics: (params = {}) => request(`/api/dashboard/analytics${query(params)}`),
  tenants: () => request("/api/tenants"),
  surveys: () => request("/api/surveys"),
  createSurvey: (payload) => request("/api/surveys", { method: "POST", body: JSON.stringify(payload) }),
  publishSurvey: (id) => request(`/api/surveys/${id}/publish`, { method: "POST" }),
  responses: (id, params = {}) => request(`/api/surveys/${id}/responses${query(params)}`),
  exportResponses: (id, format = "csv") => request(`/api/surveys/${id}/responses/export?format=${format}`, { raw: true, headers: { Accept: "*/*" } }),
  sendInvites: (payload) => request("/api/notifications/invites", { method: "POST", body: JSON.stringify(payload) }),
  openPublicSurvey: (slug, respondentKey) => {
    const query = respondentKey ? `?respondent_key=${encodeURIComponent(respondentKey)}` : "";
    return request(`/api/public/surveys/${slug}${query}`);
  },
  saveAnswer: (slug, payload) => request(`/api/public/surveys/${slug}/answers`, {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  submitResponse: (slug, payload) => request(`/api/public/surveys/${slug}/submit`, {
    method: "POST",
    body: JSON.stringify(payload),
  }),
};

function query(params) {
  const clean = Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== "");
  return clean.length ? `?${new URLSearchParams(clean).toString()}` : "";
}
