import type { Metadata } from "next";
import {
  Geist,
  Geist_Mono,
} from "next/font/google";

import { ThemeProvider } from "@/providers/ThemeProvider";

import "./globals.css";


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});


const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});


export const metadata: Metadata = {
  title: {
    default: "DeepResearch AI",
    template:
      "%s | DeepResearch AI",
  },

  description:
    "Multi-Agent AI Research & Intelligence Platform for research, critical analysis, insight generation, and structured reporting.",

  applicationName:
    "DeepResearch AI",

  icons: {
    icon: "/icon.svg",
    apple: "/icon.svg",
  },
};


export default function RootLayout({
  children,
}: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable}`}
    >
      <body>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}