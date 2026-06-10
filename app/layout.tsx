import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "GenLayer Consensus Simulator",
    template: "%s | GenLayer Consensus Simulator",
  },
  description:
    "An interactive educational platform for understanding GenLayer Intelligent Contracts, Optimistic Democracy, and Subjective Consensus.",
  keywords: [
    "GenLayer",
    "Intelligent Contracts",
    "Optimistic Democracy",
    "Blockchain",
    "Consensus",
    "Validators",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
