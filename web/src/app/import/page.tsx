"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";

const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleFileSelect = (selectedFile: File) => {
    if (selectedFile.type === "application/json" || selectedFile.name.endsWith(".json")) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError("Please select a JSON file");
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleImport = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const text = await file.text();
      const jsonData = JSON.parse(text);

      const response = await fetch(`${apiBase}/import/json`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonData),
      });

      if (!response.ok) {
        throw new Error(`Import failed: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Import failed");
    } finally {
      setLoading(false);
    }
  };

  const viewSong = () => {
    if (result?.song_id) {
      router.push(`/songs/${result.song_id}/timeline`);
    }
  };

  return (
    <main className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Import Song</h1>
        <p className="text-gray-600 mt-2">
          Import Isophonics format JSON files with chords, lyrics, and structure
        </p>
      </div>

      {/* File Drop Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="space-y-4">
          <div className="text-4xl">📄</div>
          <div>
            <p className="text-lg">
              Drop your JSON file here or{" "}
              <label className="text-blue-600 hover:text-blue-800 cursor-pointer underline">
                browse
                <input
                  type="file"
                  accept=".json"
                  onChange={(e) => e.target.files && handleFileSelect(e.target.files[0])}
                  className="hidden"
                />
              </label>
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Supports Isophonics format with chords, lyrics, and structure
            </p>
          </div>
        </div>
      </div>

      {/* Selected File */}
      {file && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{file.name}</p>
              <p className="text-sm text-gray-500">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              onClick={() => setFile(null)}
              className="text-red-600 hover:text-red-800"
            >
              Remove
            </button>
          </div>
        </div>
      )}

      {/* Import Button */}
      {file && (
        <div className="mt-6">
          <button
            onClick={handleImport}
            disabled={loading}
            className={`px-6 py-3 rounded-lg font-medium ${
              loading
                ? "bg-gray-300 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
          >
            {loading ? "Importing..." : "Import Song"}
          </button>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Success Result */}
      {result && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-green-800 font-medium">✅ Import successful!</p>
              <p className="text-green-700 mt-1">{result.message}</p>
              <p className="text-sm text-green-600 mt-2">
                Song ID: {result.song_id}
              </p>
            </div>
            <button
              onClick={viewSong}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              View Timeline
            </button>
          </div>
        </div>
      )}

      {/* Sample Files Info */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">Sample Files Available</h3>
        <p className="text-blue-800 text-sm">
          Try importing one of the Beatles sample files from the{" "}
          <code className="bg-blue-100 px-1 rounded">test_data</code> directory:
        </p>
        <ul className="text-blue-700 text-sm mt-2 space-y-1">
          <li>• hey_jude.json - Complex song with bridge and outro</li>
          <li>• let_it_be.json - Classic structure with guitar solo</li>
          <li>• yesterday.json - Simple verse/bridge structure</li>
        </ul>
      </div>
    </main>
  );
}
