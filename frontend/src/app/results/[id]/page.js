'use client';

import '../../i18n';
import { Trans, useTranslation } from 'react-i18next';
import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { BACKEND_ADDRESS } from '@/app/resources/ResourcesPaths';
import PageTitle from '../../components/PageTitle';
import BigBlueButton from '../../components/BigBlueButton';

// Fixed English metric names
const metricLabel = {
  accuracy: 'Accuracy',
  exact_match: 'Exact Match',
  f1: 'F1 Score',
  pearsonr: 'Pearson Correlation',
};
const getReadableMetricName = (metricKey) =>
  metricLabel[metricKey] ||
  metricKey.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

export default function ResultsPage() {
  const { t } = useTranslation();
  const { id: submissionId } = useParams();
  const [data, setData] = useState(null);
  const [failed, setFailed] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);
  const [downloading, setDownloading] = useState(false);
  const [downloadFailed, setDownloadFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetch(`${BACKEND_ADDRESS}/results/${submissionId}.json`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json) => {
        if (!cancelled) setData(json);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });
    return () => {
      cancelled = true;
    };
  }, [submissionId, reloadKey]);

  const retry = useCallback(() => {
    setFailed(false);
    setData(null);
    setReloadKey((k) => k + 1);
  }, []);

  const handleDownload = async () => {
    setDownloadFailed(false);
    setDownloading(true);
    try {
      const res = await fetch(`${BACKEND_ADDRESS}/results/${submissionId}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${submissionId}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch {
      setDownloadFailed(true);
    } finally {
      setDownloading(false);
    }
  };

  const tasksArray = data?.tasks || [];
  const displayName = data?.display_name || data?.config_general?.display_name;

  // The title is always rendered; the live regions stay mounted and only
  // their content changes between loading, error and loaded.
  return (
    <div className="max-w-[72ch] py-3">
      <PageTitle>
        {data
          ? t('results_page_title', { displayName: displayName || submissionId })
          : t('nav_results')}
      </PageTitle>

      <div role="status">
        {!data && !failed && <p className="text-gray-700">{t('results_loading')}</p>}
      </div>
      <div role="alert">
        {failed && (
          <div className="space-y-4">
            <p className="text-red-700">{t('results_error')}</p>
            <BigBlueButton variant="secondary" onClick={retry}>
              {t('results_retry')}
            </BigBlueButton>
          </div>
        )}
      </div>

      {data && (
        <>
          <div className="mb-6">
            <BigBlueButton variant="secondary" onClick={handleDownload} disabled={downloading}>
              {downloading ? t('results_downloading') : t('results_download')}
            </BigBlueButton>
            <div role="alert">
              {downloadFailed && (
                <p className="mt-2 text-sm font-medium text-red-700">{t('results_downloadError')}</p>
              )}
            </div>
          </div>

          {tasksArray.length === 0 ? (
            <p className="text-gray-700">
              <Trans
                i18nKey="results_no_results"
                components={[
                  <Link
                    key="guide"
                    href="/guide"
                    className="text-blue-700 underline hover:text-blue-900"
                  />,
                ]}
              />
            </p>
          ) : (
            <div className="space-y-6">
              {tasksArray.map((taskObj) => {
                const [taskName, metricsObj] = Object.entries(taskObj)[0];
                const [metricType, metricValues] = Object.entries(metricsObj)[0];
                const prettyName = taskName.split('|')[1] || taskName;
                const warningKey = `${metricType}_warning`;

                return (
                  <div
                    key={taskName}
                    className="p-5 border border-gray-200 rounded-lg shadow-sm bg-white"
                  >
                    <h2 className="text-xl font-semibold text-blue-700 mb-3">
                      {t('results_benchmark_label', { name: prettyName })}
                    </h2>
                    <ul className="list-disc ml-6 text-gray-700">
                      {Object.entries(metricValues)
                        .filter(([k]) => !k.endsWith('_warning'))
                        .map(([metricKey, value]) => (
                          <li key={metricKey}>
                            <strong>{getReadableMetricName(metricKey)}</strong>:{' '}
                            {typeof value === 'number' ? (
                              (metricKey === 'exact_match' || metricKey === 'f1'
                                ? value
                                : value * 100
                              ).toFixed(1) + '%'
                            ) : (
                              value
                            )}
                          </li>
                        ))}
                    </ul>
                    {metricValues[warningKey] && (
                      <p className="text-sm text-yellow-800 mt-2">
                        <strong>{t('results_warning')}</strong> {metricValues[warningKey]}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
