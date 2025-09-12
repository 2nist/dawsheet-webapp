import { useRouter } from "next/router";
import { useEffect } from "react";
import Link from "next/link";

export default function HomePage() {
  const router = useRouter();

  // Auto-redirect to library after 2 seconds, or user can click
  useEffect(() => {
    const timer = setTimeout(() => {
      router.push('/songs');
    }, 2000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <main className="min-h-screen p-6 flex items-center justify-center font-typewriter">
      <div className="max-w-2xl w-full">
        <div className="border border-black/15 rounded-[6px] bg-[#efe3cc] text-black shadow-[0_1px_0_rgba(0,0,0,.25)] p-8 text-center">
          <div className="flex items-center justify-center gap-2 mb-6">
            <span className="font-dymo bg-[#1a1a1a] text-[#efe3cc] rounded-[6px] px-2 py-0.5">[daw]</span>
            <h1 className="font-typewriter text-black font-bold">DAWSheet</h1>
          </div>

          <div className="space-y-6">
            <p className="font-typewriter text-black">
              A comprehensive music arrangement and timeline tool for the modern studio
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/songs" className="btn-tape-wide">
                LIBRARY
              </Link>

              <Link href="/editor" className="btn-tape-wide">
                NEW SONG
              </Link>

              <Link href="/import" className="btn-tape-wide">
                IMPORT
              </Link>
            </div>

            <div className="mt-6 p-3 border border-black/10 rounded bg-white/50">
              <p className="font-typewriter text-black">
                Redirecting to Library in 2 seconds...
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
