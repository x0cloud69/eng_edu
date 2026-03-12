/**
 * usePagination(initialPage, initialSize)
 */

import { useState, useCallback } from "react";

export function usePagination(initialPage = 1, initialSize = 20) {
  const [page, setPage] = useState(initialPage);
  const [size, setSize] = useState(initialSize);

  const nextPage = useCallback(() => setPage((p) => p + 1), []);
  const prevPage = useCallback(() => setPage((p) => Math.max(1, p - 1)), []);
  const setPageSize = useCallback((s: number) => {
    setSize(s);
    setPage(1);
  }, []);

  return { page, size, setPage, setPageSize, nextPage, prevPage };
}
