import { useState, useEffect, useCallback, useRef } from 'react';
import type { DataMetadata, TimePeriod } from '../types/api';

interface UseMetricDataReturn<T> {
  data: T | null;
  allTimeData: T | null;
  period: TimePeriod;
  setPeriod: (p: TimePeriod) => void;
  loading: boolean;
  error: string | null;
  metadata: DataMetadata;
  refresh: () => void;
}

export function useMetricData<T>(
  handle: string,
  fetchFn: (
    handle: string,
    preferFresh: boolean,
    period: TimePeriod
  ) => Promise<{ data: T; metadata: DataMetadata }>
): UseMetricDataReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [allTimeData, setAllTimeData] = useState<T | null>(null);
  const [period, setPeriod] = useState<TimePeriod>('all_time');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<DataMetadata>({ isStale: false });

  const prevHandleRef = useRef(handle);

  useEffect(() => {
    if (prevHandleRef.current !== handle) {
      setData(null);
      setAllTimeData(null);
      setError(null);
      setMetadata({ isStale: false });
      setPeriod('all_time');
      prevHandleRef.current = handle;
    }
  }, [handle]);

  useEffect(() => {
    if (!handle) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchFn(handle, false, period)
      .then((result) => {
        if (!cancelled) {
          setData(result.data);
          setMetadata(result.metadata);
          if (period === 'all_time') {
            setAllTimeData(result.data);
          }
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Failed to fetch data. Please check the handle and try again.'
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [handle, period, fetchFn]);

  const refresh = useCallback(() => {
    if (!handle) return;

    setLoading(true);
    setError(null);

    fetchFn(handle, true, period)
      .then((result) => {
        setData(result.data);
        setMetadata(result.metadata);
        if (period === 'all_time') {
          setAllTimeData(result.data);
        }
      })
      .catch((err) => {
        setError(
          err instanceof Error
            ? err.message
            : 'Failed to fetch data. Please check the handle and try again.'
        );
      })
      .finally(() => {
        setLoading(false);
      });
  }, [handle, period, fetchFn]);

  return { data, allTimeData, period, setPeriod, loading, error, metadata, refresh };
}
