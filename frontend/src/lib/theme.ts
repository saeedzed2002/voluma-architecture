export type ThemeMode = "system" | "light" | "dark";

export const themeStorageKey = "voluma-theme";

export const themeInitScript = `(function(){try{var k='${themeStorageKey}';var m=localStorage.getItem(k)||'system';if(m!=='light'&&m!=='dark'&&m!=='system')m='system';var d=m==='system'?(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'):m;var e=document.documentElement;e.dataset.theme=d;e.dataset.themeMode=m;e.style.colorScheme=d;}catch(_){document.documentElement.dataset.theme='light';document.documentElement.dataset.themeMode='system';document.documentElement.style.colorScheme='light';}})();`;
