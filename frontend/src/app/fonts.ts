import localFont from "next/font/local";

export const instrumentSans = localFont({
  src: "./fonts/InstrumentSans-Variable.woff2",
  display: "swap",
  style: "normal",
  variable: "--font-instrument-sans",
  weight: "400 700",
});

export const vazirmatn = localFont({
  src: "./fonts/Vazirmatn-Variable.woff2",
  display: "swap",
  style: "normal",
  variable: "--font-vazirmatn",
  weight: "100 900",
});
