"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getToken, clearToken } from "@/lib/auth";
import { askQuestion, getTopics } from "@/lib/api";
import { TOPIC_LABELS } from "@/lib/topics";
import UploadModal from "@/components/UploadModal";

type Source = { filename: string; page_number: number };

export default function HomePage() {
  const router = useRouter();
  const [token, setTokenState] = useState<string | null>(null);
  const [checked, setChecked] = useState(false);

  const [topics, setTopics] = useState<string[]>([]);
  const [topic, setTopic] = useState("");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    const t = getToken();
    if (!t) {
      router.push("/login");
      return;
    }
    setTokenState(t);
    setChecked(true);

    getTopics()
      .then((res) => {
        setTopics(res.topics);
        setTopic(res.topics[0] ?? "");
      })
      .catch(() => {
        // A failed topics fetch isn't fatal -- the dropdown just stays
        // empty, which is visible on its own without a separate error banner.
      });
  }, [router]);

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    if (!token || !topic || !query.trim()) return;
    setAsking(true);
    setError(null);
    setAnswer(null);
    setSources([]);
    try {
      const result = await askQuestion(topic, query, token);
      setAnswer(result.answer);
      setSources(result.sources);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setAsking(false);
    }
  }

  if (!checked || !token) {
    return null;
  }

  return (
    <div className="min-h-screen bg-zinc-50 px-4 py-10 dark:bg-black">
      <div className="mx-auto flex w-full max-w-2xl flex-col gap-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
            Network Docs Assistant
          </h1>
          <div className="flex gap-2">
            <button
              onClick={() => setShowUpload(true)}
              className="rounded-full border border-black/[.08] px-4 py-2 text-sm text-black dark:border-white/[.145] dark:text-zinc-50"
            >
              Upload document
            </button>
            <button
              onClick={handleLogout}
              className="rounded-full border border-black/[.08] px-4 py-2 text-sm text-black dark:border-white/[.145] dark:text-zinc-50"
            >
              Log out
            </button>
          </div>
        </div>

        <form
          onSubmit={handleAsk}
          className="flex flex-col gap-3 rounded-lg border border-black/[.08] bg-white p-6 dark:border-white/[.145] dark:bg-zinc-950"
        >
          <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Topic
          </label>
          <select
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="rounded border border-black/[.08] px-3 py-2 text-black dark:border-white/[.145] dark:bg-black dark:text-zinc-50"
          >
            {topics.length === 0 && (
              <option value="">Loading topics...</option>
            )}
            {topics.map((t) => (
              <option key={t} value={t}>
                {TOPIC_LABELS[t] ?? t}
              </option>
            ))}
          </select>

          <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Question
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={3}
            required
            className="rounded border border-black/[.08] px-3 py-2 text-black dark:border-white/[.145] dark:bg-black dark:text-zinc-50"
            placeholder="e.g. What is OSNR?"
          />

          <button
            type="submit"
            disabled={asking || !topic}
            className="self-start rounded-full bg-foreground px-5 py-2 font-medium text-background transition-colors hover:bg-[#383838] disabled:opacity-50 dark:hover:bg-[#ccc]"
          >
            {asking ? "Asking..." : "Ask"}
          </button>
        </form>

        {error && (
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        )}

        {answer && (
          <div className="rounded-lg border border-black/[.08] bg-white p-6 dark:border-white/[.145] dark:bg-zinc-950">
            <p className="whitespace-pre-wrap text-black dark:text-zinc-50">
              {answer}
            </p>

            {sources.length > 0 && (
              <div className="mt-4 border-t border-black/[.08] pt-4 dark:border-white/[.145]">
                <p className="mb-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  Sources
                </p>
                <ul className="flex flex-col gap-1 text-sm text-zinc-600 dark:text-zinc-400">
                  {sources.map((s, i) => (
                    <li key={i}>
                      {s.filename} — page {s.page_number}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {showUpload && token && (
        <UploadModal
          token={token}
          topics={topics}
          onClose={() => setShowUpload(false)}
        />
      )}
    </div>
  );
}
