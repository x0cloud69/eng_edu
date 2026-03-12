/**
 * axios 인스턴스 + 인터셉터 (Zustand에서 Access Token, 401 시 Refresh)
 */

import axios, { type AxiosInstance } from "axios";
import { useAuthStore } from "@/stores/authStore";

const instance: AxiosInstance = axios.create({
  baseURL: "",
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

instance.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

instance.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      // TODO: refresh token 호출 후 setAccessToken, 원래 요청 재시도
      useAuthStore.getState().logout();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default instance;
