"use client";
import { useEffect, useId, useRef } from "react";
import BigBlueButton from "./BigBlueButton";
import { useTranslation } from "react-i18next";

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

const SIZES = { md: "max-w-md", lg: "max-w-2xl" };

// Scroll lock shared by every open modal: the original overflow is saved by
// the first one and restored by the last one, whatever the unmount order.
let openModals = 0;
let savedOverflow = "";

const lockScroll = () => {
  if (openModals === 0) savedOverflow = document.body.style.overflow;
  openModals += 1;
  document.body.style.overflow = "hidden";
};

const unlockScroll = () => {
  openModals = Math.max(0, openModals - 1);
  if (openModals === 0) document.body.style.overflow = savedOverflow;
};

// When the opener lives in the collapsed mobile menu it cannot take focus;
// fall back to the menu button.
const restoreFocus = (opener) => {
  const usable =
    opener instanceof HTMLElement &&
    opener !== document.body && // the opener was hidden before the modal read focus
    opener.isConnected &&
    opener.getClientRects().length > 0;
  const target =
    usable
      ? opener
      : document.querySelector("[data-menu-toggle]");
  if (target instanceof HTMLElement && target.getClientRects().length > 0) target.focus();
};

export default function Modal({ title, children, onClose, size = "md", dismissible = true }) {
  const { t } = useTranslation();
  const titleId = useId();
  const panelRef = useRef(null);
  const onCloseRef = useRef(onClose);
  const dismissibleRef = useRef(dismissible);

  useEffect(() => {
    onCloseRef.current = onClose;
    dismissibleRef.current = dismissible;
  });

  // Move focus into the dialog, lock page scroll, restore both on unmount.
  useEffect(() => {
    const opener = document.activeElement;
    lockScroll();
    panelRef.current?.focus();
    return () => {
      unlockScroll();
      restoreFocus(opener);
    };
  }, []);

  // Listen on the document so Escape and the Tab trap keep working when
  // focus falls back to <body> (for example when the focused button unmounts).
  useEffect(() => {
    const handleKeyDown = (e) => {
      const panel = panelRef.current;
      if (!panel) return;
      if (e.key === "Escape") {
        e.stopPropagation();
        if (dismissibleRef.current) onCloseRef.current();
        return;
      }
      if (e.key !== "Tab") return;
      const focusable = Array.from(panel.querySelectorAll(FOCUSABLE));
      if (focusable.length === 0) {
        e.preventDefault();
        panel.focus();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const active = document.activeElement;
      if (!panel.contains(active)) {
        e.preventDefault();
        (e.shiftKey ? last : first).focus();
      } else if (e.shiftKey && (active === first || active === panel)) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && active === last) {
        e.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4"
      onMouseDown={(e) => { if (e.target === e.currentTarget && dismissible) onClose(); }}
    >
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
        className={`max-h-[90dvh] w-full ${SIZES[size]} overflow-y-auto rounded-xl bg-white p-6 text-gray-900 shadow-xl outline-none`}
      >
        <h2 id={titleId} className="mb-6 text-2xl font-semibold text-gray-900">
          {title}
        </h2>
        {children}
        <div className="mt-4 flex justify-end">
          <BigBlueButton variant="secondary" onClick={onClose} disabled={!dismissible}>
            {t("close")}
          </BigBlueButton>
        </div>
      </div>
    </div>
  );
}
