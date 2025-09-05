import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: 24, fontFamily: "system-ui" }}>
      <h1>DAWSheet</h1>
      <ul>
        <li>
          <Link href="/import">Import</Link>
        </li>
        <li>
          <Link href="/songs">Songs</Link>
        </li>
      </ul>
    </main>
  );
}
