import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BEM 100 v2.0 — Indian Stock Momentum Intelligence",
  description: "Production-grade Indian equity momentum and breakout screening platform.",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "BEM 100",
  },
};

export const viewport: Viewport = {
  themeColor: "#080c14",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192.svg" />
      </head>
      <body className="min-h-screen bg-[#080c14] text-slate-100 antialiased selection:bg-emerald-500 selection:text-black">
        {/* Mobile Viewport Wrapper: 375px–430px priority phone layout */}
        <div className="w-full max-w-md mx-auto min-h-screen flex flex-col border-x border-slate-800/40 shadow-2xl relative">
          <main className="flex-1 pb-16">{children}</main>
        </div>

        {/* Service Worker Auto Registration */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js').then(
                    function(registration) {
                      console.log('BEM 100 PWA ServiceWorker registered: ', registration.scope);
                    },
                    function(err) {
                      console.log('BEM 100 PWA ServiceWorker registration failed: ', err);
                    }
                  );
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
}
