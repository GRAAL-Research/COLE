'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import Modal from './Modal';
import SubmitForm from './SubmitForm';

export default function ModalManager() {
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
        <Modal onClose={handleClose}>
          <SubmitForm />
        </Modal>
      )}
    </>
  );
}
