"use client";

import { useState } from "react";
import { uploadDocument } from "@/lib/api";
import { TOPIC_LABELS } from "@/lib/topics";

export default function UploadModal({
  token,
  topics,
  onClose,
}: {
  token: string;
  topics: string[];
  onClose: () => void;
}) {
  const [topic, setTopic] = useState(topics[0] ?? "");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">(
    "idle"
  );
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !topic) return;
    setStatus("uploading");
    setMessage(null);
    try {
      const result = await uploadDocument(topic, file, token);
      setStatus("done");
      setMessage(
        `Uploaded successfully -- ${result.chunks_inserted} chunks added under "${TOPIC_LABELS[result.topic] ?? result.topic}".`
      );
    } catch (err) {
      setStatus("error");
      setMessage(err instanceof Error ? err.message : "Upload failed");
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
      <div className="w-full max-w-sm rounded-lg bg-white p-6 dark:bg-zinc-950">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-black dark:text-zinc-50">
            Upload a document
          </h2>
          <button
            onClick={onClose}
            className="text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Topic
          </label>
          <select
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="mb-4 w-full rounded border border-black/[.08] px-3 py-2 text-black dark:border-white/[.145] dark:bg-black dark:text-zinc-50"
          >
            {topics.map((t) => (
              <option key={t} value={t}>
                {TOPIC_LABELS[t] ?? t}
              </option>
            ))}
          </select>

          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
            PDF file
          </label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            required
            className="mb-4 w-full text-sm text-black dark:text-zinc-50"
          />

          {message && (
            <p
              className={`mb-4 text-sm ${
                status === "error"
                  ? "text-red-600 dark:text-red-400"
                  : "text-green-600 dark:text-green-400"
              }`}
            >
              {message}
            </p>
          )}

          <button
            type="submit"
            disabled={status === "uploading" || !file}
            className="w-full rounded-full bg-foreground px-5 py-3 font-medium text-background transition-colors hover:bg-[#383838] disabled:opacity-50 dark:hover:bg-[#ccc]"
          >
            {status === "uploading" ? "Uploading..." : "Upload"}
          </button>
        </form>
      </div>
    </div>
  );
}
