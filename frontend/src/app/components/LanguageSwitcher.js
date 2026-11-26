'use client';

import {useTranslation} from 'react-i18next';

const LANGUAGES = [
    {code: 'en', label: 'EN', name: 'English'},
    {code: 'fr', label: 'FR', name: 'Français'},
];

export function LanguageSwitcher() {
    const {t, i18n} = useTranslation();
    const currentLang = i18n.language?.startsWith('fr') ? 'fr' : 'en';

    const btnStyle = (lng) =>
        `inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg border px-2 text-sm ${
            lng === currentLang
                ? 'border-blue-600 bg-blue-600 font-semibold text-white'
                : 'border-gray-300 text-gray-700 hover:border-gray-500'
        }`;

    return (
        <div role="group" aria-label={t('lang_switcher')} className="flex shrink-0 space-x-1">
            {LANGUAGES.map(({code, label, name}) => (
                <button
                    key={code}
                    type="button"
                    lang={code}
                    aria-label={name}
                    aria-pressed={code === currentLang}
                    onClick={() => i18n.changeLanguage(code)}
                    className={btnStyle(code)}
                >
                    {label}
                </button>
            ))}
        </div>
    );
}
