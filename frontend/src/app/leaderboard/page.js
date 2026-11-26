'use client';

import React, { useEffect, useState } from "react";
import {
  normalizeBenchmarkName,
  computeAverageScore,
} from "./util";
import { useTranslation } from "react-i18next";
import { BACKEND_ADDRESS } from "@/app/resources/ResourcesPaths";

const allowedMetrics = [
  'acc',
  'accuracy',
  'f1',
  'pearson',
  'pearsonr',
  'spearman',
  'fquad',
  'exact_match',
];

const PAGE_SIZE = 25;

export default function LeaderboardPage() {
  const { t } = useTranslation();
  const [entries, setEntries] = useState([]);
  const [benchmarks, setBenchmarks] = useState([]);
  const [sortCol, setSortCol] = useState('overall');
  const [sortOrder, setSortOrder] = useState('desc');
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [search, setSearch] = useState('');

  const headerLabels = {
    rank: t('leaderboard_rankHeader'),
    model: t('leaderboard_modelHeader'),
    overall: t('leaderboard_overallHeader'),
  };

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
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  const getCellValue = (entry, col) => {
    if (col === 'model') return entry.display_name;
    if (col === 'overall') return entry.averageScore ?? null;

    const pair = Object.entries(entry.results || {}).find(
      ([rawName]) => normalizeBenchmarkName(rawName) === col
    );
    if (!pair) return null;

    const rawValues = [];
    Object.values(pair[1]).forEach((metricGroup) => {
      if (metricGroup && typeof metricGroup === 'object') {
        Object.entries(metricGroup).forEach(([metricName, metricValue]) => {
          if (
            !metricName.includes('_warning') &&
            typeof metricValue === 'number' &&
            allowedMetrics.includes(metricName.toLowerCase())
          ) {
            rawValues.push(metricValue);
          }
        });
      }
    });

    if (rawValues.length === 0) return null;
    const normalized = rawValues.map((v) => v > 1 ? v / 100 : v);
    const avg = normalized.reduce((a, b) => a + b, 0) / normalized.length;
    return avg;
  };

  // Rank by overall score (1 = best); ties share a rank, independent of
  // the current sort column or search filter.
  const rankById = new Map();
  const ranked = entries
    .filter((e) => e.averageScore != null)
    .sort((a, b) => b.averageScore - a.averageScore);
  ranked.forEach((e, i) => {
    const prev = ranked[i - 1];
    const rank =
      prev && prev.averageScore === e.averageScore
        ? rankById.get(prev.submission_id)
        : i + 1;
    rankById.set(e.submission_id, rank);
  });

  const query = search.trim().toLowerCase();
  const filtered = query
    ? entries.filter((e) =>
        (e.display_name || '').toLowerCase().includes(query)
      )
    : entries;

  const sorted = [...filtered].sort((a, b) => {
    const va = getCellValue(a, sortCol);
    const vb = getCellValue(b, sortCol);
    if (sortCol === 'rank') {
      const ra = rankById.get(a.submission_id) ?? Infinity;
      const rb = rankById.get(b.submission_id) ?? Infinity;
      if (ra === rb) return 0;
      return sortOrder === 'asc' ? ra - rb : rb - ra;
    }
    if (sortCol === 'model') {
      if (va == null) return 1;
      if (vb == null) return -1;
      return sortOrder === 'asc'
        ? va.localeCompare(vb)
        : vb.localeCompare(va);
    }
    const na = va ?? -Infinity;
    const nb = vb ?? -Infinity;
    return sortOrder === 'asc' ? na - nb : nb - na;
  });

  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE));
  const paginatedEntries = sorted.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  );

  const handleSort = (col) => {
    if (sortCol === col) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortCol(col);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  const handleSearch = (e) => {
    setSearch(e.target.value);
    setCurrentPage(1);
  };

  const renderHeader = (col) => {
    const baseLabel = headerLabels[col] ?? col;
    const arrow = sortCol === col ? (sortOrder === 'asc' ? ' ▲' : ' ▼') : '';

    if (col === 'overall') {
      return (
        <div>
          <div onClick={() => handleSort(col)} className="cursor-pointer">
            {baseLabel}
            {arrow}
          </div>
          <div className="text-xs text-blue-100 text-center">
            {t('leaderboard_avgScoreLabel')}
          </div>
        </div>
      );
    }

    if (col === 'model' || col === 'rank') {
      return (
        <div onClick={() => handleSort(col)} className="cursor-pointer">
          {baseLabel}
          {arrow}
        </div>
      );
    }

    let metricText = '';
    const sample = entries[0];
    if (sample && sample.results) {
      const p = Object.entries(sample.results).find(
        ([raw]) => normalizeBenchmarkName(raw) === col
      );
      if (p) {
        const grp = Object.values(p[1])[0];
        if (grp) {
          const metrics = Object.keys(grp)
            .filter((m) => allowedMetrics.includes(m.toLowerCase()));
          if (metrics.length > 0) {
            metricText = ` (${metrics.join(', ')})`;
          }
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

  if (loading) {
    return (
      <div className="space-y-8">
        <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-4">
          {t('leaderboard_title')}
        </h3>
        <div className="overflow-auto">
          <div className="animate-pulse space-y-3">
            <div className="h-10 bg-blue-100 rounded w-full" />
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-8 bg-gray-100 rounded w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-4">
          {t('leaderboard_title')}
        </h3>
        <div className="text-center py-12">
          <p className="text-red-600 text-lg">{t('leaderboard_errorMessage')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
        <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-4">
        {t('leaderboard_title')}</h3>
      <input
        type="search"
        value={search}
        onChange={handleSearch}
        placeholder={t('leaderboard_searchPlaceholder')}
        aria-label={t('leaderboard_searchPlaceholder')}
        className="w-full max-w-sm border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
      />
      <div className="overflow-auto">
        <table className="min-w-full border-collapse">
          <thead>
            <tr>
              {['rank', 'model', 'overall', ...benchmarks].map((b) => (
                <th
                  key={b}
                  className="border border-gray-300 px-2 py-1 bg-blue-600 text-left text-sm font-semibold text-white"
                >
                  {renderHeader(b)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedEntries.map((entry) => (
              <tr
                key={entry.submission_id}
                className="bg-white hover:bg-gray-50 cursor-pointer"
                onClick={() => setSelectedEntry(entry)}
              >
                <td className="border border-gray-300 px-2 py-1 text-center font-bold text-gray-800">
                  {rankById.get(entry.submission_id) ?? '—'}
                </td>
                <td className="border border-gray-300 px-2 py-1 font-medium text-blue-600">
                  {entry.display_name}
                </td>
                <td className="border border-gray-300 px-2 py-1 text-center text-black font-bold">
                  {entry.averageScore == null
                    ? t('leaderboard_notSpecified')
                    : (entry.averageScore * 100).toFixed(1) + '%'}
                </td>
                {benchmarks.map((b) => {
                  const val = getCellValue(entry, b);
                  return (
                    <td
                      key={b}
                      className="border border-gray-200 px-2 py-1 text-center text-gray-800"
                      title={val == null ? t('leaderboard_notSpecifiedTooltip') : undefined}
                    >
                      {val == null
                        ? <span className="text-gray-400 italic">{t('leaderboard_notSpecified')}</span>
                        : (val * 100).toFixed(1) + '%'}
                    </td>
                  );
                })}
              </tr>
            ))}
            {paginatedEntries.length === 0 && (
              <tr>
                <td
                  colSpan={benchmarks.length + 3}
                  className="px-2 py-4 text-center text-gray-500"
                >
                  {t('leaderboard_noResults')}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 py-4">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="px-3 py-1 rounded bg-blue-600 text-white disabled:opacity-40 hover:bg-blue-700 transition"
          >
            &laquo;
          </button>
          <span className="text-gray-700 text-sm">
            {currentPage} / {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="px-3 py-1 rounded bg-blue-600 text-white disabled:opacity-40 hover:bg-blue-700 transition"
          >
            &raquo;
          </button>
        </div>
      )}

      {selectedEntry && (
        <div
          className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50"
          onClick={(e) => { if (e.target === e.currentTarget) setSelectedEntry(null); }}
          onKeyDown={(e) => { if (e.key === 'Escape') setSelectedEntry(null); }}
          role="dialog"
          aria-modal="true"
          tabIndex={-1}
        >
          <div className="bg-white p-6 rounded-2xl shadow-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              {t('leaderboard_modalTitle', {
                name: selectedEntry.display_name,
              })}
            </h3>
            {Object.entries(selectedEntry.results || {}).map(
              ([taskKey, metricsObj]) => {
                const prettyName = taskKey.split('|')[1] || taskKey;
                const [metricType, values] = Object.entries(metricsObj)[0];
                return (
                  <div key={taskKey} className="mb-4">
                    <h4 className="font-medium text-blue-700">
                      {prettyName}
                    </h4>
                    <ul className="list-disc list-inside text-gray-700">
                      {Object.entries(values)
                        .filter(([k]) => !k.endsWith('_warning'))
                        .map(([metricKey, value]) => (
                          <li key={metricKey}>
                            <strong>{metricKey.replace(/_/g, ' ')}</strong>:{' '}
                            {typeof value === 'number'
                              ? (value > 1
                                ? value.toFixed(1) + '%'
                                : (value * 100).toFixed(1) + '%')
                              : value}
                          </li>
                        ))}
                    </ul>
                    {values[`${metricType}_warning`] && (
                      <p className="text-sm text-yellow-700 mt-2">
                        ⚠️ {values[`${metricType}_warning`]}
                      </p>
                    )}
                  </div>
                );
              }
            )}
            <button
              className="mt-4 px-4 py-2 bg-gray-200 rounded-full hover:bg-gray-300"
              onClick={() => setSelectedEntry(null)}
            >
              {t('leaderboard_closeButton')}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
