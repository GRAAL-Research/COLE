"use client";
import { useEffect, useState } from "react";

export default function LeaderboardPage() {
  const [entries, setEntries] = useState([]);
  const [benchmarks, setBenchmarks] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/leaderboard")
      .then((res) => res.json())
      .then((data) => {
        setEntries(data);

        const allBenchmarks = new Set();
        data.forEach((entry) => {
          Object.keys(entry.results || {}).forEach((bench) => {
            allBenchmarks.add(bench);
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
              <th className="border border-blue-500 px-2 py-1 text-left text-sm">
                Submission
              </th>
              {benchmarks.map((b, i) => (
                <th
                  key={i}
                  className="border border-blue-500 px-2 py-1 text-sm"
                >
                  {b}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {entries.map((entry, rowIndex) => (
              <tr key={rowIndex} className="bg-white hover:bg-gray-50">
                <td className="border border-gray-300 px-2 py-1 font-medium text-blue-600 text-sm">
                  {entry.zip_filename || entry.name.replace(".json", "")}

                </td>
                {benchmarks.map((b, colIndex) => {
                  const scoreDict = entry.results?.[b];
                  const scoreVal = scoreDict
                    ? Object.values(scoreDict)[0]
                    : "-";
                  return (
                    <td
                      key={colIndex}
                      className="border border-gray-200 px-2 py-1 text-center text-sm"
                    >
                      {typeof scoreVal === "number"
                        ? scoreVal.toFixed(3)
                        : scoreVal}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
