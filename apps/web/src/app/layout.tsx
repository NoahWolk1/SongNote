import type { Metadata } from "next";
import { Inter, Lato, Montserrat } from "next/font/google";
import { cn } from "@/lib/utils";
import "./globals.css";
import ConvexClientProvider from "./ConvexClientProvider";
import { AudioManagerProvider } from "@/components/common/AudioManager";

const inter = Inter({ subsets: ["latin"] });
const montserrat = Montserrat({ subsets: ["latin"] });
const lato = Lato({ weight: "400", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Lyrics Studio",
  description: "Write lyrics and turn them into songs with AI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={cn(inter.className, montserrat.className, lato.className)}
      >
        <ConvexClientProvider>
          <AudioManagerProvider>
            {children}
          </AudioManagerProvider>
        </ConvexClientProvider>
      </body>
    </html>
  );
}
