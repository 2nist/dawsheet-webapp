import type { AppProps } from "next/app";
import Link from "next/link";
import { useRouter } from "next/router";
import "../src/styles/globals.css";

function ViewTab() {
  const router = useRouter();
  const items: Array<{ label: string; href: string; functional: boolean }> = [
    { label: "Import", href: "/import", functional: true },
    { label: "Library", href: "/library", functional: true },
    { label: "Timeline", href: "/songs", functional: true }, // songs list -> pick song timeline
    { label: "Record", href: "/record", functional: true },
    { label: "Songs", href: "/songs", functional: true },
    { label: "Design", href: "/design", functional: false },
  ];
  return (
    <div className="w-full sticky top-0 z-40 bg-slate-900/90 backdrop-blur border-b border-slate-700">
      <div className="max-w-6xl mx-auto px-3 py-2 flex items-center gap-2">
        <span className="text-xs uppercase tracking-wide text-slate-300 mr-2">
          View Tab
        </span>
        {items.map((it) => {
          const active =
            router.pathname === it.href ||
            router.pathname.startsWith(it.href + "/");
          const cls = active
            ? "bg-slate-700 text-white border-slate-400"
            : "bg-slate-800 text-slate-200 border-slate-600 hover:bg-slate-700";
          return (
            <Link key={it.label} href={it.href} legacyBehavior>
              <a
                className={`text-sm px-3 py-1 rounded border ${cls} ${
                  it.functional ? "" : "opacity-60 cursor-not-allowed"
                }`}
                aria-disabled={!it.functional}
                onClick={(e) => {
                  if (!it.functional) e.preventDefault();
                }}
                title={it.functional ? it.label : `${it.label} (coming soon)`}
              >
                {it.label}
              </a>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className="min-h-screen bg-bg text-fg">
      <ViewTab />
      <div className="max-w-6xl mx-auto px-3 py-3">
        <Component {...pageProps} />
      </div>
    </div>
  );
}
