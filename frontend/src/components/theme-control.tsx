"use client";

import { useCallback, useEffect, useSyncExternalStore } from "react";

import type { ThemeMode } from "@/lib/theme";
import { themeStorageKey } from "@/lib/theme";

import { ThemeIcon } from "./icons";

const modes: ThemeMode[] = ["system", "light", "dark"];
const themeChangeEvent = "voluma-theme-change";

type ThemeControlProps = {
  labels: Record<ThemeMode, string>;
};

function applyTheme(mode: ThemeMode) {
  const resolved =
    mode === "system"
      ? window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
      : mode;

  document.documentElement.dataset.theme = resolved;
  document.documentElement.dataset.themeMode = mode;
  document.documentElement.style.colorScheme = resolved;
}

function getThemeMode(): ThemeMode {
  const activeMode = document.documentElement.dataset.themeMode;
  return modes.includes(activeMode as ThemeMode) ? (activeMode as ThemeMode) : "system";
}

function subscribeToTheme(onStoreChange: () => void) {
  window.addEventListener("storage", onStoreChange);
  window.addEventListener(themeChangeEvent, onStoreChange);

  return () => {
    window.removeEventListener("storage", onStoreChange);
    window.removeEventListener(themeChangeEvent, onStoreChange);
  };
}

export function ThemeControl({ labels }: ThemeControlProps) {
  const mode = useSyncExternalStore<ThemeMode>(
    subscribeToTheme,
    getThemeMode,
    () => "system",
  );

  useEffect(() => {
    const query = window.matchMedia("(prefers-color-scheme: dark)");
    const syncSystemTheme = () => {
      if (mode === "system") applyTheme("system");
    };
    query.addEventListener("change", syncSystemTheme);
    return () => query.removeEventListener("change", syncSystemTheme);
  }, [mode]);

  const cycleTheme = useCallback(() => {
    const nextMode = modes[(modes.indexOf(mode) + 1) % modes.length];
    window.localStorage.setItem(themeStorageKey, nextMode);
    applyTheme(nextMode);
    window.dispatchEvent(new Event(themeChangeEvent));
  }, [mode]);

  return (
    <button
      aria-label={labels[mode]}
      className="theme-control"
      data-mode={mode}
      onClick={cycleTheme}
      title={labels[mode]}
      type="button"
    >
      <ThemeIcon className="control-icon" mode={mode} />
    </button>
  );
}
