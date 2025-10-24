'use client';

import {useTranslation} from 'react-i18next';

export function LanguageSwitcher() {
    const {i18n} = useTranslation();

    const changeLanguage = (lng) => {
        i18n.changeLanguage(lng);
    };

    return (
        <div className="flex space-x-2">
            <button onClick={() => changeLanguage('en')} className="px-2 py-1 rounded-lg border"
                    className="px-3 py-1.5 rounded-lg border bg-blue-600 text-white hover:bg-blue-700 transition-fr">
                EN
            </button>
            <button onClick={() => changeLanguage('fr')} className="px-2 py-1 rounded-lg border"
                    className="px-3 py-1.5 rounded-lg border bg-blue-600 text-white hover:bg-blue-700 transition-en">
                FR
            </button>
        </div>
    );
}
