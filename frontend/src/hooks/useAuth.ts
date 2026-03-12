/**
 * useMe, useLogout 등 인증 훅
 */

import { useAuthStore } from "@/stores/authStore";

export function useMe() {
  return useAuthStore((s) => s.user);
}

export function useLogout() {
  return useAuthStore((s) => s.logout);
}
