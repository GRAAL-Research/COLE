"use client";

import { useEffect, useState } from "react";
import { use } from "react"; // Next.js 15+

export default function ResultsPage({ params }) {
  const { id: submissionId } = use(params);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const localKey = `results_${submissionId}`;
    const cached = localStorage.getItem(localKey);

    if (cached) {
      setData(JSON.parse(cached));
      return;
    }

    const url = `http://localhost:8000/results/${submissionId}.json`;
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then((json) => {
        setData(json);
        localStorage.setItem(localKey, JSON.stringify(json));
      })
      .catch((err) => setError(err.message));
  }, [submissionId]);

  useEffect(() => {
    if (!data) return;

    const downloadKey = `downloaded_${submissionId}`;
    const alreadyDownloaded = localStorage.getItem(downloadKey);

    const file = data.file || `${submissionId}.json`;

    if (!alreadyDownloaded && file) {
      const link = document.createElement("a");
      link.href = `http://localhost:8000/results/${file}`;
      link.download = file;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      localStorage.setItem(downloadKey, "true");
    }
  }, [data, submissionId]);

  if (error) {
    return (
      <main className="max-w-3xl mx-auto px-6 py-6 text-center">
        <p className="text-red-600 font-semibold text-lg">❌ Error: {error}</p>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="max-w-3xl mx-auto px-6 py-6 text-center">
        <p className="text-gray-600">⏳ Loading results...</p>
      </main>
    );
  }

  const results = data.results || {};
  const keys = Object.keys(results);

  return (
    <main className="max-w-3xl mx-auto px-6 py-6">
      <h2 className="text-2xl font-bold text-center mb-6">
        <span className="text-blue-700">📊 Results for </span>
        <span className="text-gray-800">{data.email}</span>
      </h2>

      {keys.length === 0 ? (
        <p className="text-blue-700 text-center">
          ⚠️ No benchmark results found.
        </p>
      ) : (
        <div className="space-y-6">
          {keys.map((benchmark) => (
            <div
              key={benchmark}
              className="p-5 border border-purple-400 rounded-xl shadow-md bg-white"
            >
              <h3 className="text-xl font-semibold text-blue-700 mb-3">
                🧪 Benchmark: {benchmark}
              </h3>
              <ul className="list-disc ml-6 text-gray-700">
                {Object.entries(results[benchmark]).map(([metric, value]) => (
                  <li key={metric}>
                    <strong>{metric}</strong>:{" "}
                    {typeof value === "number" ? value.toFixed(3) : value}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
