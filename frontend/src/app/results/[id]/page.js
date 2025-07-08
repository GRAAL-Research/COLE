"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";

const metricLabel = {
  accuracy: "Accuracy",
  exact_match: "Exact Match",
  f1: "F1 Score",
  pearsonr: "Pearson Correlation",
};

const getReadableMetricName = (metricKey) =>
  metricLabel[metricKey] ||
  metricKey.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

export default function ResultsPage() {
  const { id: submissionId } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    fetch(`http://localhost:8000/results/${submissionId}.json`)
      .then((res) => {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, [submissionId]);
 const handleDownload = async () => {
 if (!data) return;
  try {
    const res = await fetch(`http://localhost:8000/results/${submissionId}.json`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const blob = await res.blob();

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `${submissionId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  } catch (e) {
    console.error("Download failed:", e);
  }
};

  if (!data) {
    return (
      <main className="max-w-3xl mx-auto px-6 py-6 text-center">
        <p className="text-gray-600">⏳ Loading results...</p>
      </main>
    );
  }

  const tasksArray = data.tasks || [];
  const displayName = data.display_name || data.config_general?.display_name;

  return (
    <main className="max-w-3xl mx-auto px-6 py-6">
      <h2 className="text-2xl font-bold text-center mb-4">
        <span className="text-blue-700">📊 Results for </span>
        <span className="text-gray-800">{displayName}</span>
      </h2>

      <div className="flex justify-center mb-6">
        <button
          onClick={handleDownload}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition"
        >
          Download JSON
        </button>
      </div>

      {tasksArray.length === 0 ? (
        <p className="text-blue-700 text-center">
          ⚠️ No benchmark results found.
        </p>
      ) : (
        <div className="space-y-6">
          {tasksArray.map((taskObj) => {
            const [taskName, metricsObj] = Object.entries(taskObj)[0];
            const [metricType, metricValues] = Object.entries(metricsObj)[0];
            const prettyName = taskName.split("|")[1] || taskName;
            const warningKey = `${metricType}_warning`;

            return (
              <div
                key={taskName}
                className="p-5 border border-purple-400 rounded-xl shadow-md bg-white"
              >
                <h3 className="text-xl font-semibold text-blue-700 mb-3">
                  🧪 Benchmark: {prettyName}
                </h3>
                <ul className="list-disc ml-6 text-gray-700">
                  {Object.entries(metricValues)
                    .filter(([k]) => !k.endsWith("_warning"))
                    .map(([metricKey, value]) => (
                      <li key={metricKey}>
                        <strong>{getReadableMetricName(metricKey)}</strong>:{" "}
                        {typeof value === "number" ? (
                          (metricKey === "exact_match" || metricKey === "f1"
                            ? value
                            : value * 100
                          ).toFixed(1) + "%"
                        ) : (
                          value
                        )}
                      </li>
                    ))}
                </ul>
                {metricValues[warningKey] && (
                  <p className="text-sm text-yellow-700 mt-2">
                    ⚠️ {metricValues[warningKey]}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
}
