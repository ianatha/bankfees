import type { Metadata } from "next";
import { Fira_Mono, Fira_Sans } from "next/font/google";
import "./globals.css";

const fontSans = Fira_Sans({
  variable: "--font-fira-sans",
  subsets: ["latin", "greek"],
  weight: ["400", "700"],
});

const fontMono = Fira_Mono({
  variable: "--font-fira-mono",
  subsets: ["latin", "greek"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "Έρευνα Τραπεζικών Χρεώσεων",
  description: "Ευρετήριο τραπεζικών εγγράφων για αναζήτηση χρεώσεων",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${fontSans.variable} ${fontMono.variable} antialiased font-sans`}
      >
        {children}
      </body>
    </html>
  );
}
