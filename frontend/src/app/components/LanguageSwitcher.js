'use client';

import {useTranslation} from 'react-i18next';

export function LanguageSwitcher() {
    const {i18n} = useTranslation();
    const currentLang = i18n.language?.startsWith('fr') ? 'fr' : 'en';

    const btnStyle = (lng) =>
        lng === currentLang
            ? 'px-2 py-1 rounded-lg border-2 border-blue-600 bg-blue-600 text-white font-semibold'
            : 'px-2 py-1 rounded-lg border border-gray-300 text-gray-500 hover:border-gray-400';

    return (
        <div className="flex space-x-1">
            <button onClick={() => i18n.changeLanguage('en')} className={btnStyle('en')}>
                EN
            </button>
            <button onClick={() => i18n.changeLanguage('fr')} className={btnStyle('fr')}>
                FR
            </button>
        </div>
    );
}
