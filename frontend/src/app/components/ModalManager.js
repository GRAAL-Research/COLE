'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import Modal from './Modal';
import SubmitForm from './SubmitForm';

export default function ModalManager() {
  const { t } = useTranslation();
  const searchParams = useSearchParams();
  const submitModal = searchParams.get("show") === "submit";
  const router = useRouter();

  const handleClose = () => {
    const newUrl = window.location.pathname;
    router.push(newUrl);
  };

  return (
    <>
      {submitModal && (
        <Modal title={t('submit_formTitle')} onClose={handleClose}>
          <SubmitForm />
        </Modal>
      )}
    </>
  );
}
