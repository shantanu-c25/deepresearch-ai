"use client";

import {
  createContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type {
  ResolvedTheme,
  ThemePreference,
} from "@/types/theme";


const THEME_STORAGE_KEY =
  "deepresearch-theme";


export type ThemeContextValue = {
  preference: ThemePreference;
  resolvedTheme: ResolvedTheme;
  setPreference: (
    preference: ThemePreference
  ) => void;
};


export const ThemeContext =
  createContext<ThemeContextValue | null>(
    null
  );


type ThemeProviderProps = {
  children: ReactNode;
};


function supportsMatchMedia(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function"
  );
}


function getSystemTheme(): ResolvedTheme {
  if (
    supportsMatchMedia() &&
    window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches
  ) {
    return "dark";
  }

  return "light";
}


function applyTheme(
  preference: ThemePreference
) {
  const root =
    document.documentElement;

  if (preference === "system") {
    root.removeAttribute(
      "data-theme"
    );

    return;
  }

  root.setAttribute(
    "data-theme",
    preference
  );
}


export function ThemeProvider({
  children,
}: ThemeProviderProps) {
  const [
    preference,
    setPreferenceState,
  ] = useState<ThemePreference>(
    "system"
  );

  const [
    systemTheme,
    setSystemTheme,
  ] = useState<ResolvedTheme>(
    "light"
  );


  useEffect(() => {
    const savedPreference =
      window.localStorage.getItem(
        THEME_STORAGE_KEY
      ) as ThemePreference | null;

    const initialPreference =
      savedPreference === "light" ||
      savedPreference === "dark" ||
      savedPreference === "system"
        ? savedPreference
        : "system";

    setPreferenceState(
      initialPreference
    );

    setSystemTheme(
      getSystemTheme()
    );

    applyTheme(
      initialPreference
    );
  }, []);


  useEffect(() => {
    if (!supportsMatchMedia()) {
      return;
    }

    const mediaQuery =
      window.matchMedia(
        "(prefers-color-scheme: dark)"
      );


    function handleSystemThemeChange() {
      setSystemTheme(
        mediaQuery.matches
          ? "dark"
          : "light"
      );
    }


    mediaQuery.addEventListener(
      "change",
      handleSystemThemeChange
    );


    return () => {
      mediaQuery.removeEventListener(
        "change",
        handleSystemThemeChange
      );
    };
  }, []);


  function setPreference(
    nextPreference: ThemePreference
  ) {
    setPreferenceState(
      nextPreference
    );

    window.localStorage.setItem(
      THEME_STORAGE_KEY,
      nextPreference
    );

    applyTheme(
      nextPreference
    );
  }


  const resolvedTheme: ResolvedTheme =
    preference === "system"
      ? systemTheme
      : preference;


  const value = useMemo(
    () => ({
      preference,
      resolvedTheme,
      setPreference,
    }),
    [
      preference,
      resolvedTheme,
    ]
  );


  return (
    <ThemeContext.Provider
      value={value}
    >
      {children}
    </ThemeContext.Provider>
  );
}