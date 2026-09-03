import { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';

interface UseVirtualTableOptions<T> {
  data: T[] | undefined;
  estimateSize?: number;
  overscan?: number;
}

export function useVirtualTable<T>({
  data = [],
  estimateSize = 42,
  overscan = 5,
}: UseVirtualTableOptions<T>) {
  const parentRef = useRef<HTMLDivElement | null>(null);

  const rowVirtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => estimateSize,
    overscan,
  });

  return {
    parentRef,
    rowVirtualizer,
    virtualRows: rowVirtualizer.getVirtualItems(),
    totalSize: rowVirtualizer.getTotalSize(),
  };
}
