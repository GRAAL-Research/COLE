'use client';

import React, { useEffect, useState } from 'react';
import { use } from 'react';

const metricLabel = {
  acc: "Accuracy",
  acc_stderr: "Standard Error",
  f1: "F1 Score",
  pearson: "Pearson Correlation",
  spearman: "Spearman Correlation",
};

const getReadableMetricName = (metric) => {
  return (
    metricLabel[metric] ||
    metric
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase())
  );
};

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

  const handleDownload = () => {
    if (!data) return;
    const fileName = data.file || `${submissionId}.json`;
    const downloadUrl = `http://localhost:8000/results/${fileName}`;

    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (error) {
    return (
      <main className="max-w-3xl mx-auto px-6 py-6 text-center">
        <p className="text-red-600 font-semibold text-lg">
          ❌ Error: {error}
        </p>
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
  const taskResults = Object.entries(results).filter(([key]) => key !== "all");
  const globalMetrics = results["all"] || {};
  const displayName =
    data.config_general?.model_name || data.display_name || data.email;

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
          ️ Download JSON
        </button>
      </div>

      {Object.keys(globalMetrics).length > 0 && (
        <div className="mb-6 p-5 bg-blue-50 border border-blue-300 rounded-md">
          <h3 className="text-lg font-semibold text-blue-700 mb-2">
            🌐 Global Score
          </h3>
          <ul className="ml-4 text-sm text-gray-700 list-disc">
            {Object.entries(globalMetrics).map(([metric, value]) => (
              <li key={metric}>
                <strong>{getReadableMetricName(metric)}</strong>:{" "}
                {typeof value === "number"
                  ? (value * 100).toFixed(1) + "%"
                  : value}
              </li>
            ))}
          </ul>
        </div>
      )}

      {taskResults.length === 0 ? (
        <p className="text-blue-700 text-center">
          ⚠️ No benchmark results found.
        </p>
      ) : (
        <div className="space-y-6">
          {taskResults.map(([key, metrics]) => {
            const prettyName = key.split("|")[1] || key;
            return (
              <div
                key={key}
                className="p-5 border border-purple-400 rounded-xl shadow-md bg-white"
              >
                <h3 className="text-xl font-semibold text-blue-700 mb-3">
                  🧪 Benchmark: {prettyName}
                </h3>
                <ul className="list-disc ml-6 text-gray-700">
                  {Object.entries(metrics).map(([metric, value]) => (
                    <li key={metric}>
                      <strong>{getReadableMetricName(metric)}</strong>:{" "}
                      {typeof value === "number"
                        ? (value * 100).toFixed(1) + "%"
                        : value}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
}
