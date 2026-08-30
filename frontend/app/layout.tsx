import type { Metadata, Viewport } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import "./globals.css";

export const metadata: Metadata = {
  title: "BizReg | Business Registration",
  description: "Digital business-registration public service platform",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        <SiteHeader />
        {children}
        <footer className="border-t border-slate-200 bg-slate-900 px-6 py-10 text-slate-400">
          <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-4 text-sm sm:flex-row">
            <span className="font-bold text-white tracking-tight">BizReg</span>
            <span>Digital Public Services Platform · SecureAI Labs</span>
            <span>© {new Date().getFullYear()} — Learning project</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
