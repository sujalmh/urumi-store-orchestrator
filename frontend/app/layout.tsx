import "./globals.css";
import { Space_Grotesk, Source_Sans_3 } from "next/font/google";

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-display" });
const sourceSans = Source_Sans_3({ subsets: ["latin"], variable: "--font-body" });

export const metadata = {
  title: "Store Provisioning",
  description: "Provision isolated WooCommerce stores",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${spaceGrotesk.variable} ${sourceSans.variable} bg-fog text-ink`}>
        {children}
      </body>
    </html>
  );
}
