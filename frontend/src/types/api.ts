/**
 * Backend ApiResponse와 1:1 대응 TypeScript 타입
 */

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: PaginatedData<T> | null;
}

export interface ApiError {
  code: string;
  message: string;
  request_id?: string;
  timestamp?: string;
}

export interface ApiErrorResponse {
  success: false;
  error: ApiError;
}
