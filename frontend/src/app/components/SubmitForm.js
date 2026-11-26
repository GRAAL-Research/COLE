'use client';

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import ErrorMessage from "./ErrorMessage";
import { BACKEND_ADDRESS } from "@/app/resources/ResourcesPaths";
import BigBlueButton from "./BigBlueButton";
import { Trans, useTranslation } from 'react-i18next';

const INPUT_CLASS =
  "w-full rounded-md border border-gray-400 p-3 text-gray-900 aria-[invalid=true]:border-red-700";

const FILE_INPUT_CLASS =
  `${INPUT_CLASS} cursor-pointer p-2 text-sm text-gray-700 file:mr-3 file:cursor-pointer file:rounded-md file:border-0 file:bg-blue-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-blue-800 hover:file:bg-blue-100`;

export default function SubmitForm({ onStateChange }) {
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

  const emailRef = useRef(null);
  const displayNameRef = useRef(null);
  const fileRef = useRef(null);
  const feedbackRef = useRef(null);

  const isDirty = submitStatus !== 'success' && Boolean(email || displayName || file);

  useEffect(() => {
    onStateChange?.({ isSubmitting, isDirty });
  }, [isSubmitting, isDirty, onStateChange]);

  // The form is gone with its modal: report a clean state to the parent.
  useEffect(
    () => () => onStateChange?.({ isSubmitting: false, isDirty: false }),
    [onStateChange]
  );

  // Focus would otherwise fall to <body> when the submit button is disabled or
  // the form is hidden; move it to the result so keyboard users stay in the dialog.
  useEffect(() => {
    if (submitStatus) feedbackRef.current?.focus();
  }, [submitStatus]);

  const validate = () => {
    const errors = {};
    if (!email.trim() || !/^\S+@\S+\.\S+$/.test(email.trim())) errors.email = t('submit_errorEmail');
    if (!displayName.trim()) errors.displayName = t('submit_errorDisplayName');
    if (!file) errors.file = t('submit_errorZip');
    else if (!file.name.toLowerCase().endsWith('.zip')) errors.file = t('submit_zipAlert');
    return errors;
  };

  const clearFieldError = (name) =>
    setFieldErrors((prev) => (prev[name] ? { ...prev, [name]: undefined } : prev));

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errors = validate();
    setFieldErrors(errors);
    const firstInvalid = ['email', 'displayName', 'file'].find((k) => errors[k]);
    if (firstInvalid) {
      const refsByField = { email: emailRef, displayName: displayNameRef, file: fileRef };
      refsByField[firstInvalid].current?.focus();
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
      const offline = err instanceof TypeError || navigator.onLine === false;
      setErrorMessage(
        offline
          ? t('submit_errorOffline')
          : t('submit_errorMessage', {
              errorMessage: String(err.message).replace(/[.\s]+$/, ''),
            })
      );
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const field = (name, id, label, input, hint) => (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-gray-800">
        {label}
      </label>
      {hint}
      {input}
      <ErrorMessage id={`${id}-error`}>{fieldErrors[name]}</ErrorMessage>
    </div>
  );

  const aria = (name, id, extraDescribedBy) => {
    const describedBy = [extraDescribedBy, fieldErrors[name] ? `${id}-error` : null]
      .filter(Boolean)
      .join(' ');
    return {
      'aria-invalid': fieldErrors[name] ? 'true' : undefined,
      'aria-describedby': describedBy || undefined,
    };
  };

  return (
    <div className="space-y-5">
      <form
        onSubmit={handleSubmit}
        noValidate
        hidden={submitStatus === 'success'}
        className="space-y-5"
      >
        {field('email', 'email', t('submit_labelEmail'),
          <input
            id="email"
            ref={emailRef}
            type="email"
            autoComplete="email"
            required
            placeholder={t('submit_placeholderEmail')}
            value={email}
            onChange={(e) => { setEmail(e.target.value); clearFieldError('email'); }}
            className={INPUT_CLASS}
            {...aria('email', 'email')}
          />
        )}
        {field('displayName', 'displayname', t('submit_labelDisplayName'),
          <input
            id="displayname"
            ref={displayNameRef}
            type="text"
            required
            placeholder={t('submit_placeholderDisplayName')}
            value={displayName}
            onChange={(e) => { setDisplayName(e.target.value); clearFieldError('displayName'); }}
            className={INPUT_CLASS}
            {...aria('displayName', 'displayname')}
          />
        )}
        {field('file', 'zipfile', t('submit_labelZip'),
          <input
            id="zipfile"
            ref={fileRef}
            type="file"
            accept=".zip"
            required
            onChange={(e) => { setFile(e.target.files[0] ?? null); clearFieldError('file'); }}
            className={FILE_INPUT_CLASS}
            {...aria('file', 'zipfile', 'zipfile-hint')}
          />,
          <p id="zipfile-hint" className="mb-2 text-sm text-gray-700">
            <Trans
              i18nKey="submit_zipHint"
              components={[
                <a
                  key="guide"
                  href="/guide"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-700 underline hover:text-blue-900"
                />,
              ]}
            />
            <span className="sr-only"> {t('nav_newTab')}</span>
          </p>
        )}

        <BigBlueButton type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? t('submit_submitting') : t('submit_button')}
        </BigBlueButton>
      </form>

      {/* Both live regions stay mounted so their text is announced when it changes. */}
      <div ref={feedbackRef} tabIndex={-1} className="space-y-4 outline-none">
        <div role="status" className="space-y-4">
          {isSubmitting && <p className="sr-only">{t('submit_submitting')}</p>}
          {submitStatus === 'success' && (
            <>
              <p className="text-lg font-semibold text-green-800">{t('submit_successTitle')}</p>
              <p className="text-gray-700">{t('submit_successMessage')}</p>
              <BigBlueButton onClick={() => router.push(`/results/${submissionId}`)}>
                {t('submit_checkResults')}
              </BigBlueButton>
            </>
          )}
        </div>
        <div role="alert">
          {submitStatus === 'error' && (
            <p className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-800">
              {errorMessage}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
