import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SongGraph MVP",
  description: "Phase 0 scaffold for SongGraph webapp",
};

type RootLayoutProps = Readonly<{ children: React.ReactNode }>;

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

