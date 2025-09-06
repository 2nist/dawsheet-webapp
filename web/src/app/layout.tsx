import "../styles/globals.css";

export const metadata = {
  title: "DAWSheet",
  description: "Design and analysis workbench",
};

export default function RootLayout({ children }: { children: any }) {
  return (
    <html lang="en">
      <body className="bg-bg text-fg min-h-screen">{children}</body>
    </html>
  );
}
