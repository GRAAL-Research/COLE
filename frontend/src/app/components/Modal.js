"use client";
import BigBlueButton from "./BigBlueButton";
import { useTranslation } from "react-i18next";

export default function Modal({ children, onClose }) {
  const { t } = useTranslation();

  return (
    <div
      className="fixed inset-0 bg-gray-600 bg-opacity-25 overflow-y-auto h-full w-full flex items-center justify-center z-50"
      style={{ backgroundColor: 'rgba(75, 85, 99, 0.55)' }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      onKeyDown={(e) => { if (e.key === 'Escape') onClose(); }}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
    >
      <div className="p-8 border w-96 shadow-lg rounded-md bg-white">
        <div className="text-center text-black">
          {children}
          <div className="flex justify-center mt-4">
            <BigBlueButton onClick={onClose}>
              {t('close')}
            </BigBlueButton>
          </div>
        </div>
      </div>
    </div>
  );
}
