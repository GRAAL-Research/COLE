'use client';

import { useCallback, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import Modal from './Modal';
import SubmitForm from './SubmitForm';

const IDLE_FORM = { isSubmitting: false, isDirty: false };

export default function ModalManager() {
  const { t } = useTranslation();
  const searchParams = useSearchParams();
  const submitModal = searchParams.get("show") === "submit";
  const router = useRouter();
  const [formState, setFormState] = useState(IDLE_FORM);

  const handleFormState = useCallback((next) => setFormState(next), []);

  const handleClose = () => {
    if (formState.isSubmitting) return;
    if (formState.isDirty && !window.confirm(t('submit_confirmDiscard'))) return;
    router.push(window.location.pathname);
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
