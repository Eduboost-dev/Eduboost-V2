import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import { LearnerProvider } from "@/context/LearnerContext";
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
    default: "EduBoost SA — Modern Learning for South African Students",
    template: "%s | EduBoost SA",
  },
  description:
    "EduBoost SA is a professional EdTech platform delivering CAPS-aligned learning for South African primary school students.",
  keywords: ["education", "South Africa", "CAPS", "learning", "EdTech", "Grade 4"],
  authors: [{ name: "EduBoost SA" }],
  creator: "EduBoost SA",
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3050"),
  openGraph: {
    type: "website",
    locale: "en_ZA",
    siteName: "EduBoost SA",
    title: "EduBoost SA — Modern Learning for South African Students",
    description: "Professional CAPS-aligned learning platform for SA primary education.",
  },
  twitter: {
    card: "summary_large_image",
    title: "EduBoost SA",
    description: "Professional CAPS-aligned learning platform for SA primary education.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
  },
};

export const viewport: Viewport = {
  themeColor: "#0a1628",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-background text-foreground`}
        suppressHydrationWarning
      >
        <LearnerProvider>
          {children}
        </LearnerProvider>
        <Toaster position="bottom-right" theme="dark" />
      </body>
    </html>
  );
}

