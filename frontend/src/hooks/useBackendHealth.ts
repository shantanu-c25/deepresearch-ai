"use client";

import {
  useEffect,
  useState,
} from "react";

import { getHealth } from "@/lib/api";


export type BackendStatus =
  | "checking"
  | "connected"
  | "unavailable"
  | "offline";


export function useBackendHealth() {
  const [
    status,
    setStatus,
  ] = useState<BackendStatus>(
    "checking"
  );


  useEffect(() => {
    let isMounted = true;


    async function checkBackend() {
      try {
        const health =
          await getHealth();

        if (!isMounted) {
          return;
        }

        setStatus(
          health.status === "ok"
            ? "connected"
            : "unavailable"
        );
      } catch {
        if (!isMounted) {
          return;
        }

        setStatus("offline");
      }
    }


    checkBackend();


    return () => {
      isMounted = false;
    };
  }, []);


  return {
    status,
  };
}