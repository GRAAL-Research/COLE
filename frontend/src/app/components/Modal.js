"use client";
import { useEffect, useId, useRef } from "react";
import BigBlueButton from "./BigBlueButton";
import { useTranslation } from "react-i18next";

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

const SIZES = { md: "max-w-md", lg: "max-w-2xl" };

export default function Modal({ title, children, onClose, size = "md" }) {
  const { t } = useTranslation();
  const titleId = useId();
  const panelRef = useRef(null);

  // Move focus into the dialog, lock page scroll, restore both on unmount.
  useEffect(() => {
    const previouslyFocused = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    panelRef.current?.focus();
    return () => {
      document.body.style.overflow = previousOverflow;
      if (previouslyFocused instanceof HTMLElement && previouslyFocused.isConnected) {
        previouslyFocused.focus();
      }
    };
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === "Escape") {
      e.stopPropagation();
      onClose();
      return;
    }
    if (e.key !== "Tab") return;
    const focusable = Array.from(panelRef.current.querySelectorAll(FOCUSABLE));
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    const active = document.activeElement;
    if (e.shiftKey && (active === first || active === panelRef.current)) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && active === last) {
      e.preventDefault();
      first.focus();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4"
      onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}
      onKeyDown={handleKeyDown}
    >
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className={`max-h-[90vh] w-full ${SIZES[size]} overflow-y-auto rounded-xl bg-white p-6 text-gray-900 shadow-xl outline-none`}
      >
        <h2 id={titleId} className="mb-6 text-2xl font-semibold text-gray-900">
          {title}
        </h2>
        {children}
        <div className="mt-4 flex justify-end">
          <BigBlueButton variant="secondary" onClick={onClose}>
            {t("close")}
          </BigBlueButton>
        </div>
      </div>
    </div>
  );
}
