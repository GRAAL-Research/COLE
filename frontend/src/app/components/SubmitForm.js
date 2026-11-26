'use client';

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import ErrorMessage from "./ErrorMessage";
import { BACKEND_ADDRESS } from "@/app/resources/ResourcesPaths";
import BigBlueButton from "./BigBlueButton";
import { useTranslation } from 'react-i18next';

const INPUT_CLASS =
  "w-full rounded-md border border-gray-400 p-3 text-gray-900 aria-[invalid=true]:border-red-700";

export default function SubmitForm() {
  const { t } = useTranslation();
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [file, setFile] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null); // 'success' | 'error'
  const [errorMessage, setErrorMessage] = useState('');
  const [submissionId, setSubmissionId] = useState(null);

  const fieldRefs = { email: useRef(null), displayName: useRef(null), file: useRef(null) };

  const validate = () => {
    const errors = {};
    if (!email.trim() || !/^\S+@\S+\.\S+$/.test(email.trim())) errors.email = t('submit_errorEmail');
    if (!displayName.trim()) errors.displayName = t('submit_errorDisplayName');
    if (!file) errors.file = t('submit_errorZip');
    else if (!file.name.toLowerCase().endsWith('.zip')) errors.file = t('submit_zipAlert');
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errors = validate();
    setFieldErrors(errors);
    const firstInvalid = ['email', 'displayName', 'file'].find((k) => errors[k]);
    if (firstInvalid) {
      fieldRefs[firstInvalid].current?.focus();
      return;
    }

    setSubmitStatus(null);
    setIsSubmitting(true);

    const formData = new FormData();
    formData.append('email', email.trim());
    formData.append('display_name', displayName.trim());
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

  if (submitStatus === 'success') {
    return (
      <div role="status" className="space-y-4">
        <p className="text-lg font-semibold text-green-800">{t('submit_successTitle')}</p>
        <p className="text-gray-700">{t('submit_successMessage')}</p>
        <BigBlueButton onClick={() => router.push(`/results/${submissionId}`)}>
          {t('submit_checkResults')}
        </BigBlueButton>
      </div>
    );
  }

  const field = (name, id, label, input) => (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-gray-800">
        {label}
      </label>
      {input}
      <ErrorMessage id={`${id}-error`}>{fieldErrors[name]}</ErrorMessage>
    </div>
  );

  const aria = (name, id) => ({
    'aria-invalid': fieldErrors[name] ? 'true' : undefined,
    'aria-describedby': fieldErrors[name] ? `${id}-error` : undefined,
  });

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-5">
      {field('email', 'email', t('submit_labelEmail'),
        <input
          id="email"
          ref={fieldRefs.email}
          type="email"
          autoComplete="email"
          required
          placeholder={t('submit_placeholderEmail')}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={INPUT_CLASS}
          {...aria('email', 'email')}
        />
      )}
      {field('displayName', 'displayname', t('submit_labelDisplayName'),
        <input
          id="displayname"
          ref={fieldRefs.displayName}
          type="text"
          required
          placeholder={t('submit_placeholderDisplayName')}
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          className={INPUT_CLASS}
          {...aria('displayName', 'displayname')}
        />
      )}
      {field('file', 'zipfile', t('submit_labelZip'),
        <input
          id="zipfile"
          ref={fieldRefs.file}
          type="file"
          accept=".zip"
          required
          onChange={(e) => setFile(e.target.files[0] ?? null)}
          className={INPUT_CLASS}
          {...aria('file', 'zipfile')}
        />
      )}

      {submitStatus === 'error' && (
        <p role="alert" className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-800">
          <strong>{t('submit_errorTitle')}</strong>{' '}
          {t('submit_errorMessage', { errorMessage })}
        </p>
      )}

      <BigBlueButton type="submit" disabled={isSubmitting} className="w-full">
        {isSubmitting ? t('submit_submitting') : t('submit_button')}
      </BigBlueButton>
    </form>
  );
}
