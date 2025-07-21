'use client';

import { useState } from "react";
import { useRouter } from "next/navigation";
import ErrorMessage from "./ErrorMessage";
import {BACKEND_ADDRESS} from "@/app/resources/ResourcesPaths";
import { Trans } from 'react-i18next';
import BigBlueButton from "./BigBlueButton";

export default function SubmitForm() {
  const { t } = useTranslation();
  const router = useRouter();

  const [requiredVisible, setRequiredVisible] = useState(false);
  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [file, setFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null); // 'success' | 'error'
  const [errorMessage, setErrorMessage] = useState('');
  const [submissionId, setSubmissionId] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const submitResults = async () => {
    if (!email || !displayName || !file) {
      setRequiredVisible(true);
      return;
    }
    if (!file.name.toLowerCase().endsWith('.zip')) {
      alert(t('submit_zipAlert'));
      return;
    }

    setRequiredVisible(false);
    setIsSubmitting(true);

    const formData = new FormData();
    formData.append('email', email);
    formData.append('display_name', displayName);
    formData.append('predictions_zip', file);

    try {
      const res = await fetch(`${BACKEND_ADDRESS}/submit`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.detail || `HTTP ${res.status}`);
      }
      const json = await res.json();
      const id = json.submission_id;
      setSubmissionId(id);
      localStorage.setItem('last_result_file', `${id}.json`);
      localStorage.setItem('just_submitted', 'true');
      setSubmitStatus('success');
    } catch (err) {
      setErrorMessage(err.message);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderModal = () => {
    if (submitStatus === 'success') {
      return (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded-2xl shadow-lg max-w-sm text-center">
            <h3 className="text-xl font-semibold text-green-600">
              {t('submit_successTitle')}
            </h3>
            <p className="mt-2">{t('submit_successMessage')}</p>
            <button
              className="mt-4 px-4 py-2 rounded-full shadow hover:shadow-md"
              onClick={() => router.push(`/results/${submissionId}`)}
            >
              {t('submit_checkResults')}
            </button>
          </div>
        </div>
      );
    }
    if (submitStatus === 'error') {
      return (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded-2xl shadow-lg max-w-sm text-center">
            <h3 className="text-xl font-semibold text-red-600">
              {t('submit_errorTitle')}
            </h3>
            <p className="mt-2">
              <Trans i18nKey="submit_errorMessage" values={{ errorMessage }}>
                Submission error: {{ errorMessage }}
              </Trans>
            </p>
            <button
              className="mt-4 px-4 py-2 rounded-full shadow hover:shadow-md"
              onClick={() => setSubmitStatus(null)}
            >
              {t('submit_closeButton')}
            </button>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="relative">
      <div className="space-y-6 bg-white rounded-xl shadow-md p-6 w-full max-w-xl mx-auto border border-gray-200">
        <h2 className="text-2xl font-semibold text-gray-800 text-center">
          {t('submit_formTitle')}
        </h2>

        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            {t('submit_labelEmail')}
          </label>
          <input
            id="email"
            type="email"
            placeholder={t('submit_placeholderEmail')}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="border border-gray-300 p-3 rounded-md w-full focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="displayname" className="block text-sm font-medium text-gray-700">
            {t('submit_labelDisplayName')}
          </label>
          <input
            id="displayname"
            type="text"
            placeholder={t('submit_placeholderDisplayName')}
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="border border-gray-300 p-3 rounded-md w-full focus:ring-2 focus:ring-blue-500"
          />
        </div>

      <ErrorMessage condition={requiredVisible}>
        ⚠️ Email, display name & ZIP are required.
      </ErrorMessage>
      {renderModal()}
    </div>
    </div>
  );}
