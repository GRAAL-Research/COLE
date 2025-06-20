"use client";
import { useEffect, useState } from "react";
import { computeRankedEntries, normalizeBenchmarkName } from "./util";
import ModelDetailsModal from "../components/ModelDetailsModal";

export default function LeaderboardPage() {
  const [entries, setEntries] = useState([]);
  const [benchmarks, setBenchmarks] = useState([]);
  const [selectedEntry, setSelectedEntry] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/leaderboard")
      .then((res) => res.json())
      .then((data) => {
        const ranked = computeRankedEntries(data);
        setEntries(ranked);

        const allBenchmarks = new Set();
        data.forEach((entry) => {
          Object.keys(entry.results || {}).forEach((bench) => {
            allBenchmarks.add(normalizeBenchmarkName(bench));
          });
        });
        setBenchmarks([...allBenchmarks]);
      })
      .catch((err) => console.error("Failed to load leaderboard:", err));
  }, []);

  return (
    <div className="w-full px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        Leaderboard
      </h2>

      <div className="w-full">
        <table className="w-full text-sm border border-blue-500 shadow-md">
          <thead>
            <tr className="bg-blue-100 text-blue-800">
              <th className="border border-blue-500 px-2 py-1 text-left text-sm">Rank</th>
              <th className="border border-blue-500 px-2 py-1 text-left text-sm">Model Name</th>
              <th className="border border-blue-500 px-2 py-1 text-sm">Score (%)</th>
              {benchmarks.map((b, i) => (
                <th key={i} className="border border-blue-500 px-2 py-1 text-sm">
                  {b} (%)
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {entries.map((entry, rowIndex) => (
              <tr key={rowIndex} className="bg-white hover:bg-gray-50">
                <td className="border border-gray-300 px-2 py-1 text-sm text-center font-bold text-purple-700">
                  {entry.rank}
                </td>
                <td
                  className="border border-gray-300 px-2 py-1 font-medium text-blue-600 text-sm cursor-pointer underline"
                  onClick={() => setSelectedEntry(entry)}
                >
                  {entry.display_name || entry.name.replace(".json", "")}
                </td>
                <td className="border border-gray-300 px-2 py-1 text-center text-sm font-semibold text-green-700">
                  {typeof entry.score === "number" ? (entry.score * 100).toFixed(1) : "-"}
                </td>
                {benchmarks.map((b, colIndex) => {
                  const scoreDict = Object.entries(entry.results || {}).find(
                    ([key]) => normalizeBenchmarkName(key) === b
                  )?.[1];

                  let scoreVal = "-";
                  if (scoreDict) {
                    const values = Object.values(scoreDict).filter((v) => typeof v === "number");
                    if (values.length > 0) {
                      const avg = values.reduce((sum, v) => sum + v, 0) / values.length;
                      scoreVal = avg * 100;
                    }
                  }

                  return (
                    <td
                      key={colIndex}
                      className="border border-gray-200 px-2 py-1 text-center text-sm"
                    >
                      {typeof scoreVal === "number" ? scoreVal.toFixed(1) : scoreVal}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedEntry && (
        <ModelDetailsModal
          entry={selectedEntry}
          onClose={() => setSelectedEntry(null)}
        />
      )}
    </div>
  );
}
