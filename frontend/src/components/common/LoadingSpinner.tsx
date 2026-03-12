export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center p-4" role="status" aria-label="로딩 중">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
    </div>
  );
}
