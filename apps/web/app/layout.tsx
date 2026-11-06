import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PROTEA - Biological Discovery Studio",
  description: "AI-Native Computational Interactomics Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#030712] text-slate-100 antialiased font-sans">
        {children}
      </body>
    </html>
  );
}
