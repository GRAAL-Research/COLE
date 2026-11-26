'use client';

import { useCallback, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import Modal from './Modal';
import SubmitForm from './SubmitForm';

const IDLE_FORM = { isSubmitting: false, isDirty: false };

export default function ModalManager() {
  const { t } = useTranslation();
  const searchParams = useSearchParams();
  const submitModal = searchParams.get("show") === "submit";
  const [formState, setFormState] = useState(IDLE_FORM);

  const handleFormState = useCallback((next) => setFormState(next), []);

  const handleClose = () => {
    if (formState.isSubmitting) return;
    if (formState.isDirty && !window.confirm(t('submit_confirmDiscard'))) return;
    // Drop only the `show` param. The page is statically prerendered, so the
    // router's canonical URL has no search string on a direct load of
    // `?show=submit`; router.push(pathname) then targets the URL the router
    // already believes it is on and silently does nothing. The native History
    // API is synced into useSearchParams by Next, so use it directly.
    const params = new URLSearchParams(window.location.search);
    params.delete("show");
    const query = params.toString();
    window.history.pushState(
      null,
      "",
      `${window.location.pathname}${query ? `?${query}` : ""}${window.location.hash}`,
    );
  };

  return (
    <>
      {submitModal && (
        <Modal
          title={t('submit_formTitle')}
          onClose={handleClose}
          dismissible={!formState.isSubmitting}
        >
          <SubmitForm onStateChange={handleFormState} />
        </Modal>
      )}
    </>
  );
}
