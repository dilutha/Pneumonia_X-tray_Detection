import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PneumoScan AI — Chest X-Ray Analysis",
  description:
    "AI-powered pneumonia detection from chest X-ray images using deep learning",
  keywords: ["pneumonia detection", "chest X-ray", "AI", "medical imaging", "CNN"],
  authors: [{ name: "PneumoScan AI" }],
  openGraph: {
    title: "PneumoScan AI",
    description: "AI-powered chest X-ray pneumonia detection",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className="font-sans bg-gray-950 text-gray-100 antialiased"
      >
        {children}
      </body>
    </html>
  );
}
