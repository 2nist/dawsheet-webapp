import { redirect } from "next/navigation";

export default function SongTimelineRedirect({
  params,
}: {
  params: { id: string };
}) {
  // Temporary: redirect to the existing song details page
  redirect(`/songs/${params.id}`);
}
