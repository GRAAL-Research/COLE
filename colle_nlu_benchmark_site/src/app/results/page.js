"use client";
import { useEffect, useState } from "react";

export default function ResultatsPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/results")
      .then((res) => {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then((data) => {
        console.log("Données reçues :", data);
        setData(data);
      })
      .catch((err) => {
        console.error("Erreur :", err);
        setError(err.message);
      });
  }, []);

  // ✅ Téléchargement automatique après chargement
  useEffect(() => {
    if (data?.file) {
      const link = document.createElement("a");
      link.href = `http://localhost:8000/results/${data.file}`;
      link.download = data.file;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }, [data]);

  if (error) {
    return (
      <main className="max-w-3xl mx-auto px-6 py-3">
        <p className="text-red-600 font-semibold">❌ Erreur : {error}</p>
      </main>
    );
  }

  if (!data) {
    return (
      <main className="max-w-3xl mx-auto px-6 py-3">
        <p className="text-gray-700">⏳ Chargement...</p>
      </main>
    );
  }

  const results = data.results;
  const benchmarkKeys = results && typeof results === "object" ? Object.keys(results) : [];

  if (benchmarkKeys.length === 0) {
    return (
      <main className="max-w-3xl mx-auto px-6 py-3">
        <p className="text-purple-700">⚠️ Aucun résultat trouvé.</p>
      </main>
    );
  }

  return (
    <main className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        📊 Résultats pour <span className="text-purple-700">{data.email}</span>
      </h2>

      <div className="space-y-8">
        {benchmarkKeys.map((benchmark) => {
          const scores = results[benchmark];
          return (
            <div
              key={benchmark}
              className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow transition"
            >
              <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-4">
                🧪 Benchmark : {benchmark}
              </h3>

              <ul className="text-gray-700 list-disc ml-6">
                {Object.entries(scores).map(([metric, value]) => (
                  <li key={metric}>
                    <strong>{metric}</strong> :{" "}
                    {typeof value === "number" ? value.toFixed(3) : value}
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    </main>
  );
}
