import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Company Research | Relu Consultancy",
  description: "AI-powered company research assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css"
        />
      </head>
      <body className="min-h-screen bg-bg text-text font-sans antialiased">{children}</body>
    </html>
  );
}