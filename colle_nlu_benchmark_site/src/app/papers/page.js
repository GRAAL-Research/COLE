'use client';

import React, { useState } from 'react';

export default function PapersPage() {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="relative h-screen">
      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-white z-10">
          <div className="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full" />
        </div>
      )}
        <div className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        Our papers
      </h2>
    </div>

      <iframe
        onLoad={() => setLoaded(true)}
        src="/COLLE.pdf"
        title="Document COLLE"
        width="100%"
        height="100%"
        className="border-none"
      />
    </div>
  );
}
