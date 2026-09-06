export type ThemeMode = "system" | "light" | "dark";

export const themeStorageKey = "voluma-theme";

export function themeInitScript(defaultMode: ThemeMode = "system") {
  return `(function(){try{var k='${themeStorageKey}';var m=localStorage.getItem(k)||'${defaultMode}';if(m!=='light'&&m!=='dark'&&m!=='system')m='${defaultMode}';var d=m==='system'?(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'):m;var e=document.documentElement;e.dataset.theme=d;e.dataset.themeMode=m;e.style.colorScheme=d;}catch(_){document.documentElement.dataset.theme='light';document.documentElement.dataset.themeMode='system';document.documentElement.style.colorScheme='light';}})();`;
}
