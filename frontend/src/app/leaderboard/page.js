"use client";


import React, { useEffect, useState } from "react";
import {
  normalizeBenchmarkName,
  computeAverageScore,
} from "./util";

import {BACKEND_ADDRESS} from "@/app/resources/ResourcesPaths";

const allowedMetrics = [
  "acc",
  "accuracy",
  "f1",
  "pearson",
  "pearsonr",
  "spearman",
];

const headerLabels = {
  model: "Model Name",
  overall: "Overall",
};

export default function LeaderboardPage() {
  const [entries, setEntries] = useState([]);
  const [benchmarks, setBenchmarks] = useState([]);
  const [sortCol, setSortCol] = useState("overall");
  const [sortOrder, setSortOrder] = useState("desc");

  useEffect(() => {
    fetch(`${BACKEND_ADDRESS}/leaderboard`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        const withOverall = data.map((e) => ({
          ...e,
          averageScore: computeAverageScore(e),
        }));
        setEntries(withOverall);

        const allBench = new Set();
        withOverall.forEach((entry) => {
          Object.keys(entry.results || {}).forEach((raw) => {
            allBench.add(normalizeBenchmarkName(raw));
          });
        });
        setBenchmarks(Array.from(allBench));
      })
      .catch((err) => console.error("Failed to load leaderboard:", err));
  }, []);

  const getCellValue = (entry, col) => {
    if (col === "model") return entry.display_name;
    if (col === "overall") return entry.averageScore ?? null;

    const pair = Object.entries(entry.results || {}).find(
      ([rawName]) => normalizeBenchmarkName(rawName) === col
    );
    if (!pair) return null;

    // 1) on collecte rawValues
    const rawValues = [];
    const taskData = pair[1];
    Object.values(taskData).forEach((metricGroup) => {
      if (metricGroup && typeof metricGroup === "object") {
        Object.entries(metricGroup).forEach(
          ([metricName, metricValue]) => {
            if (
              !metricName.includes("_warning") &&
              typeof metricValue === "number" &&
              allowedMetrics.includes(metricName.toLowerCase())
            ) {
              rawValues.push(metricValue);
            }
          }
        );
      }
    });
    if (rawValues.length === 0) return null;

    const normalized = rawValues.map((v) =>
      v > 1 ? v / 100 : v
    );
    const sum = normalized.reduce((a, b) => a + b, 0);
    return sum / normalized.length;
  };

  const sorted = [...entries].sort((a, b) => {
    const va = getCellValue(a, sortCol);
    const vb = getCellValue(b, sortCol);
    if (sortCol === "model") {
      if (va == null) return 1;
      if (vb == null) return -1;
      return sortOrder === "asc"
        ? va.localeCompare(vb)
        : vb.localeCompare(va);
    }
    const na = va ?? -Infinity;
    const nb = vb ?? -Infinity;
    return sortOrder === "asc" ? na - nb : nb - na;
  });

  const handleSort = (col) => {
    if (sortCol === col) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortCol(col);
      setSortOrder("desc");
    }
  };

  const renderHeader = (col) => {
    const baseLabel = headerLabels[col] ?? col;
    const arrow =
      sortCol === col ? (sortOrder === "asc" ? " ▲" : " ▼") : "";

    if (col === "overall") {
      return (
        <>
          <div onClick={() => handleSort(col)} className="cursor-pointer">
            {baseLabel}
            {arrow}
          </div>
          <div className="text-xs text-gray-600 text-center">
            (avg score)
          </div>
        </>
      );
    }

    let metricText = "";
    const sample = entries[0];
    if (sample && sample.results) {
      const p = Object.entries(sample.results).find(
        ([raw]) => normalizeBenchmarkName(raw) === col
      );
      if (p) {
        const grp = Object.values(p[1])[0];
        if (grp) {
          const m = Object.keys(grp).find((m) =>
            allowedMetrics.includes(m.toLowerCase())
          );
          if (m) metricText = ` (${m})`;
        }
      }
    }

    return (
      <div onClick={() => handleSort(col)} className="cursor-pointer">
        {baseLabel}
        {arrow}
        {metricText}
      </div>
    );
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Leaderboard</h1>
      <div className="overflow-auto">
        <table className="min-w-full border-collapse">
          <thead>
            <tr>
              {["model", "overall", ...benchmarks].map((b) => (
                <th
                  key={b}
                  className="border border-gray-300 px-2 py-1 bg-blue-100 text-left text-sm font-semibold text-blue-700"
                >
                  {renderHeader(b)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((entry) => (
              <tr
                key={entry.submission_id}
                className="bg-white hover:bg-gray-50"
              >
                <td className="border border-gray-300 px-2 py-1 font-medium text-blue-600">
                  {entry.display_name}
                </td>
                <td className="border border-gray-300 px-2 py-1 text-center">
                  {entry.averageScore == null
                    ? "NS"
                    : (entry.averageScore * 100).toFixed(1) + "%"}
                </td>
                {benchmarks.map((b) => {
                  const val = getCellValue(entry, b);
                  return (
                    <td
                      key={b}
                      className="border border-gray-200 px-2 py-1 text-center text-purple-700"
                    >
                      {val == null
                        ? "NS"
                        : (val * 100).toFixed(1) + "%"}
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
