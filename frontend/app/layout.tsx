import type { Metadata } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import "./globals.css";

export const metadata: Metadata = {
  title: "BizReg | Business Registration",
  description: "Digital business-registration public service platform",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900">
        <SiteHeader />
        {children}
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-sm text-slate-500">
          BizReg learning platform · SecureAI Labs
        </footer>
      </body>
    </html>
  );
}
