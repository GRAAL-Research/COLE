'use client';

import React, { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight, ChevronsUpDown, TriangleAlert } from "lucide-react";
import PageTitle from "@/app/components/PageTitle";
import Modal from "@/app/components/Modal";
import BigBlueButton, { buttonClass } from "@/app/components/BigBlueButton";
import {
  normalizeBenchmarkName,
  computeAverageScore,
  prettifyModelName,
  shortTaskName,
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

// Width of the sticky rank column; the model column is pinned right after it.
const RANK_COL_WIDTH = "5rem";

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
  const [reloadKey, setReloadKey] = useState(0);
  const [scrollState, setScrollState] = useState({ scrolled: false, atEnd: false });
  const searchRef = useRef(null);
  const scrollRef = useRef(null);
  const tableRef = useRef(null);

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
          display_name: prettifyModelName(e.display_name),
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
  }, [reloadKey]);

  const retry = () => {
    setError(false);
    setLoading(true);
    setReloadKey((k) => k + 1);
  };

  const updateScrollState = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const next = {
      scrolled: el.scrollLeft > 0,
      atEnd: el.scrollLeft + el.clientWidth >= el.scrollWidth - 1,
    };
    setScrollState((prev) =>
      prev.scrolled === next.scrolled && prev.atEnd === next.atEnd ? prev : next
    );
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

  // The scroll container only exists once rows are shown; watch its size and
  // the table's (columns and rows change both) to keep the edge cues right.
  const hasRows = sorted.length > 0;
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return undefined;
    updateScrollState();
    const observer = new ResizeObserver(updateScrollState);
    observer.observe(el);
    if (tableRef.current) observer.observe(tableRef.current);
    return () => observer.disconnect();
  }, [loading, error, hasRows, updateScrollState]);

  const stickyClass = (col, isHeader) => {
    if (col !== 'rank' && col !== 'model') return '';
    // Below sm only the model column is pinned; the rank scrolls away.
    const position =
      col === 'rank'
        ? 'sm:sticky sm:left-0 sm:z-10 w-(--rank-w) min-w-(--rank-w) max-w-(--rank-w)'
        : 'sticky z-10 left-0 sm:left-(--rank-w) min-w-40 sm:min-w-56';
    const edge = col === 'model' && scrollState.scrolled
      ? ' shadow-[4px_0_6px_-4px_rgba(0,0,0,0.35)]'
      : '';
    const background = isHeader ? '' : ' bg-white group-hover:bg-gray-50';
    return `${position}${background}${edge}`;
  };

  const renderHeader = (col) => {
    const baseLabel =
      headerLabels[col] ??
      shortTaskName(t(`benchmark_${col}_title`, { defaultValue: col }));
    const isSorted = sortCol === col;
    const SortIcon = isSorted ? (sortOrder === 'asc' ? ArrowUp : ArrowDown) : ChevronsUpDown;

    let metricText = '';
    if (col !== 'rank' && col !== 'model' && col !== 'overall') {
      const sample = entries[0];
      const p = sample?.results
        ? Object.entries(sample.results).find(([raw]) => normalizeBenchmarkName(raw) === col)
        : null;
      const grp = p ? Object.values(p[1])[0] : null;
      if (grp) {
        const metrics = Object.keys(grp).filter((m) => allowedMetrics.includes(m.toLowerCase()));
        if (metrics.length > 0) metricText = ` (${metrics.join(', ')})`;
      }
    }

    // Score columns carry the unit once in the header so cells stay bare numbers.
    const isScore = col !== 'rank' && col !== 'model';

    return (
      <>
        <button
          type="button"
          onClick={() => handleSort(col)}
          aria-label={
            isScore
              ? t('leaderboard_columnWithUnit', { name: `${baseLabel}${metricText}` })
              : undefined
          }
          className={`inline-flex min-h-11 items-center gap-1 rounded font-semibold text-white focus-visible:outline-white ${
            isScore ? 'text-right' : 'text-left'
          }`}
        >
          <span>
            {baseLabel}
            {metricText}
            {isScore && (
              <span aria-hidden="true" className="whitespace-nowrap font-normal">
                {' '}(%)
              </span>
            )}
          </span>
          <SortIcon
            className={`h-4 w-4 shrink-0 ${isSorted ? '' : 'opacity-70'}`}
            aria-hidden="true"
          />
        </button>
        {col === 'overall' && (
          <div className="text-xs font-normal text-white">{t('leaderboard_avgScoreLabel')}</div>
        )}
      </>
    );
  };

  const columns = ['rank', 'model', 'overall', ...benchmarks];
  const ariaSort = (col) =>
    sortCol === col ? (sortOrder === 'asc' ? 'ascending' : 'descending') : 'none';

  const title = <PageTitle>{t('leaderboard_title')}</PageTitle>;

  // Live regions stay mounted across states and only their text changes, so
  // screen readers announce each transition.
  const liveRegions = (
    <>
      <div role="status" aria-busy={loading} className="sr-only">
        {loading
          ? t('leaderboard_loading')
          : !error && query && sorted.length === 0
            ? t('leaderboard_noResults')
            : ''}
      </div>
      <div role="alert" className={error ? 'pt-12 text-center' : undefined}>
        {error && <p className="mb-4 text-lg text-red-700">{t('leaderboard_errorMessage')}</p>}
      </div>
    </>
  );

  if (loading) {
    return (
      <div>
        {title}
        {liveRegions}
        <div aria-hidden="true" className="animate-pulse motion-reduce:animate-none">
          <div className="mb-6 h-11 w-full max-w-sm rounded bg-gray-200" />
          <div className="overflow-hidden">
            <div className="h-14 w-max min-w-full rounded-t bg-blue-200" />
            {[...Array(8)].map((_, i) => (
              <div key={i} className="flex h-11 w-max min-w-full items-center gap-6 border-b border-gray-200 px-2">
                <div className="hidden h-4 w-8 shrink-0 rounded bg-gray-200 sm:block" />
                <div className="h-4 w-36 shrink-0 rounded bg-gray-200 sm:w-48" />
                {[...Array(10)].map((__, j) => (
                  <div key={j} className="h-4 w-16 shrink-0 rounded bg-gray-200" />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        {title}
        {liveRegions}
        <div className="pb-12 text-center">
          <BigBlueButton variant="secondary" onClick={retry}>
            {t('leaderboard_retry')}
          </BigBlueButton>
        </div>
      </div>
    );
  }

  const clearSearch = () => {
    setSearch('');
    setCurrentPage(1);
    searchRef.current?.focus();
  };

  const pagerButton =
    'inline-flex min-h-11 min-w-11 items-center justify-center rounded bg-accent text-white hover:bg-accent-strong disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-600';

  return (
    <div>
      {title}
      {liveRegions}
      {entries.length > 0 && (
        <input
          ref={searchRef}
          type="search"
          value={search}
          onChange={handleSearch}
          placeholder={t('leaderboard_searchPlaceholder')}
          aria-label={t('leaderboard_searchPlaceholder')}
          className="mb-6 min-h-11 w-full max-w-sm rounded border border-gray-400 px-3 py-2 text-base text-gray-900 sm:text-sm"
        />
      )}

      {sorted.length === 0 ? (
        <div className="py-12 text-center">
          {query ? (
            <>
              <p className="mb-4 text-gray-700">{t('leaderboard_noResults')}</p>
              <BigBlueButton variant="secondary" onClick={clearSearch}>
                {t('leaderboard_clearSearch')}
              </BigBlueButton>
            </>
          ) : (
            <>
              <p className="mb-4 text-gray-700">{t('leaderboard_empty')}</p>
              <Link href="/leaderboard?show=submit" className={buttonClass('secondary')}>
                {t('nav_submit')}
              </Link>
            </>
          )}
        </div>
      ) : (
        <div className="relative">
          <div
            ref={scrollRef}
            onScroll={updateScrollState}
            role="region"
            tabIndex={0}
            aria-label={t('leaderboard_scrollRegion')}
            className="overflow-x-auto"
          >
            <table
              ref={tableRef}
              style={{ '--rank-w': RANK_COL_WIDTH }}
              className="min-w-full border-separate border-spacing-0"
            >
              <thead>
                <tr>
                  {columns.map((b) => (
                    <th
                      key={b}
                      scope="col"
                      aria-sort={ariaSort(b)}
                      className={`border-b border-r border-blue-500 bg-blue-600 px-2 py-1 align-top text-sm text-white ${
                        b === 'rank' || b === 'model'
                          ? `text-left ${stickyClass(b, true)}`
                          : 'min-w-28 text-right'
                      }`}
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
                    className="group cursor-pointer"
                    onClick={(e) => {
                      e.currentTarget.querySelector('button')?.focus();
                      setSelectedEntry(entry);
                    }}
                  >
                    <td className={`border-b border-r border-gray-200 px-2 py-1 text-center font-bold text-gray-800 ${stickyClass('rank')}`}>
                      {rankById.get(entry.submission_id) ?? '-'}
                    </td>
                    <td className={`border-b border-r border-gray-200 px-1 py-0 font-medium ${stickyClass('model')}`}>
                      <button
                        type="button"
                        aria-haspopup="dialog"
                        aria-label={t('leaderboard_openDetails', { name: entry.display_name })}
                        title={entry.display_name}
                        onClick={(e) => {
                          e.stopPropagation();
                          // Safari and Firefox on macOS do not focus buttons on click.
                          e.currentTarget.focus();
                          setSelectedEntry(entry);
                        }}
                        className="line-clamp-2 block min-h-11 w-full max-w-[9rem] rounded px-1 text-left leading-tight wrap-anywhere text-blue-700 hover:underline sm:max-w-[20rem]"
                      >
                        {entry.display_name}
                      </button>
                    </td>
                    <td className="border-b border-r border-gray-200 bg-white px-2 py-1 text-right font-bold tabular-nums text-gray-900 group-hover:bg-gray-50">
                      {entry.averageScore == null
                        ? t('leaderboard_notSpecified')
                        : (entry.averageScore * 100).toFixed(1)}
                    </td>
                    {benchmarks.map((b) => {
                      const val = getCellValue(entry, b);
                      return (
                        <td
                          key={b}
                          className="border-b border-r border-gray-200 bg-white px-2 py-1 text-right tabular-nums text-gray-800 group-hover:bg-gray-50"
                          title={val == null ? t('leaderboard_notSpecifiedTooltip') : undefined}
                        >
                          {val == null
                            ? <span className="italic text-gray-600">{t('leaderboard_notSpecified')}</span>
                            : (val * 100).toFixed(1)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!scrollState.atEnd && (
            <div
              aria-hidden="true"
              className="pointer-events-none absolute inset-y-0 right-0 w-10 bg-linear-to-l from-black/15 to-transparent"
            />
          )}
        </div>
      )}

      {totalPages > 1 && (
        <nav
          aria-label={t('leaderboard_pagination')}
          className="flex items-center justify-center gap-4 py-4"
        >
          <button
            type="button"
            aria-label={t('leaderboard_prevPage')}
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className={pagerButton}
          >
            <ChevronLeft className="h-5 w-5" aria-hidden="true" />
          </button>
          <span className="text-sm text-gray-800" aria-live="polite" aria-atomic="true">
            {t('leaderboard_pageStatus', { current: currentPage, total: totalPages })}
          </span>
          <button
            type="button"
            aria-label={t('leaderboard_nextPage')}
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className={pagerButton}
          >
            <ChevronRight className="h-5 w-5" aria-hidden="true" />
          </button>
        </nav>
      )}

      {selectedEntry && (
        <Modal
          size="lg"
          title={t('leaderboard_modalTitle', { name: selectedEntry.display_name })}
          onClose={() => setSelectedEntry(null)}
        >
          {Object.entries(selectedEntry.results || {}).map(
            ([taskKey, metricsObj]) => {
              const prettyName = taskKey.split('|')[1] || taskKey;
              const [metricType, values] = Object.entries(metricsObj)[0];
              return (
                <div key={taskKey} className="mb-4">
                  <h3 className="font-medium text-blue-700">{prettyName}</h3>
                  <ul className="list-inside list-disc text-gray-700">
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
                    <p className="mt-2 flex items-start gap-1.5 text-sm text-yellow-800">
                      <TriangleAlert aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0" />
                      <span>{values[`${metricType}_warning`]}</span>
                    </p>
                  )}
                </div>
              );
            }
          )}
        </Modal>
      )}
    </div>
  );
}
