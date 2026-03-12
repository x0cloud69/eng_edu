/**
 * React Query QueryClient 설정
 */

import { QueryClient } from "@tanstack/react-query";

const STALE = 1000 * 60 * 5;   // 5분
const GC = 1000 * 60 * 10;     // 10분

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: STALE,
      gcTime: GC,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
