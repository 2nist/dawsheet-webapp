import { useEffect, useRef, useState } from "react";
import Link from "next/link";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function RecordPage() {
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [deviceId, setDeviceId] = useState<string | undefined>(undefined);
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);

  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then((list) => {
      setDevices(list.filter((d) => d.kind === "audioinput"));
    });
  }, []);

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: deviceId ? { deviceId: { exact: deviceId } } : true,
    });
    const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mr.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
    };
    mr.onstop = onStop; // finalize
    mediaRecorderRef.current = mr;
    chunksRef.current = [];
    mr.start();
    setRecording(true);
    // setup analyser for waveform
    audioCtxRef.current = new (window.AudioContext ||
      (window as any).webkitAudioContext)();
    analyserRef.current = audioCtxRef.current.createAnalyser();
    analyserRef.current.fftSize = 2048;
    sourceRef.current = audioCtxRef.current.createMediaStreamSource(stream);
    sourceRef.current.connect(analyserRef.current);
    draw();
  }

  function stop() {
    mediaRecorderRef.current?.stop();
    mediaRecorderRef.current?.stream.getTracks().forEach((t) => t.stop());
    setRecording(false);
  }

  function draw() {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    if (!canvas || !analyser) return;
    const ctx = canvas.getContext("2d")!;
    const bufferLength = analyser.fftSize;
    const dataArray = new Uint8Array(bufferLength);
    const render = () => {
      if (!analyser) return;
      analyser.getByteTimeDomainData(dataArray);
      ctx.fillStyle = "#0f172a";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.lineWidth = 2;
      ctx.strokeStyle = "#6ee7b7";
      ctx.beginPath();
      const sliceWidth = (canvas.width * 1.0) / bufferLength;
      let x = 0;
      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
        x += sliceWidth;
      }
      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
      requestAnimationFrame(render);
    };
    requestAnimationFrame(render);
  }

  async function onStop() {
    const blob = new Blob(chunksRef.current, { type: "audio/webm" });
    const form = new FormData();
    form.append("file", blob, "recording.webm");
    const res = await fetch(`${apiBase}/recordings/upload`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) {
      alert(`Upload failed: ${await res.text()}`);
      return;
    }
    const { jobId } = await res.json();
    // poll job
    const id = setInterval(async () => {
      const jr = await fetch(`${apiBase}/jobs/${jobId}`);
      if (!jr.ok) return;
      const data = await jr.json();
      if (data.status === "done" && data.draftId) {
        clearInterval(id);
        window.location.href = `/songs/from-draft/${data.draftId}`;
      }
    }, 1500);
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Record</h1>
      <div
        style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 8 }}
      >
        <label>
          Input:
          <select
            value={deviceId}
            onChange={(e) => setDeviceId(e.target.value)}
            style={{ marginLeft: 8 }}
          >
            <option value="">Default</option>
            {devices.map((d) => (
              <option key={d.deviceId} value={d.deviceId}>
                {d.label || d.deviceId}
              </option>
            ))}
          </select>
        </label>
        {!recording ? (
          <button onClick={start}>Record</button>
        ) : (
          <button onClick={stop}>Stop</button>
        )}
        <Link href="/">Home</Link>
      </div>
      <div style={{ marginTop: 16 }}>
        <canvas
          ref={canvasRef}
          width={800}
          height={200}
          style={{
            border: "1px solid #1f2937",
            background: "#0f172a",
            borderRadius: 6,
          }}
        />
      </div>
      <p style={{ marginTop: 8, color: "#9aa3af" }}>
        {recording ? "Recording…" : "Idle"}
      </p>
    </main>
  );
}
