import "../styles/globals.css";
import Link from "next/link";

export const metadata = { title: "DAWSheet" };
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="sticky top-0 z-10 border-b border-border bg-bg/80 backdrop-blur">
          <nav className="mx-auto max-w-6xl flex items-center gap-4 px-4 py-3 text-sm">
            <Link href="/" className="font-semibold">
              DAWSheet
            </Link>
            <Link href="/import" className="opacity-90 hover:opacity-100">
              Import
            </Link>
            <Link href="/songs" className="opacity-90 hover:opacity-100">
              Songs
            </Link>
            <Link href="/record" className="opacity-90 hover:opacity-100">
              Record
            </Link>
            <Link href="/library" className="opacity-90 hover:opacity-100">
              Library
            </Link>
            <Link
              href="/design"
              className="ml-auto opacity-90 hover:opacity-100"
            >
              Design
            </Link>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
      </body>
    </html>
  );
}
