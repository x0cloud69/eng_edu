/**
 * API 엔드포인트 상수
 */

const API_BASE = "/api/v1";

export const ENDPOINTS = {
  health: "/health",
  auth: {
    login: `${API_BASE}/auth/login`,
    logout: `${API_BASE}/auth/logout`,
    refresh: `${API_BASE}/auth/refresh`,
    me: `${API_BASE}/auth/me`,
  },
} as const;
