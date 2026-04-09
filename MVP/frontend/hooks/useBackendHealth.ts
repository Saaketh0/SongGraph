"use client";

import { useEffect, useState } from "react";

import { fetchBackendHealth } from "../lib/api";

export type HealthSummary = {
  status: string;
  detail: string;
};

const initialHealth: HealthSummary = {
  status: "loading",
  detail: "Checking...",
};

export function useBackendHealth(): HealthSummary {
  const [health, setHealth] = useState<HealthSummary>(initialHealth);

  useEffect(() => {
    let cancelled = false;

    async function loadHealth() {
      try {
        const payload = await fetchBackendHealth();
        if (cancelled) {
          return;
        }
        setHealth({
          status: payload.status ?? "unknown",
          detail: `${payload.service ?? "backend"} (${payload.environment ?? "n/a"})`,
        });
      } catch (error) {
        if (cancelled) {
          return;
        }
        setHealth({
          status: "unavailable",
          detail: error instanceof Error ? error.message : "Backend not reachable",
        });
      }
    }

    loadHealth();
    return () => {
      cancelled = true;
    };
  }, []);

  return health;
}
