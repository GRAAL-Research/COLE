'use client';
import { useState } from 'react';

const faqs = [
  {
    question: "How can I evaluate my model?",
    answer: "You can upload your model outputs in JSON format on the website. The system will automatically evaluate them, and you can view the results in the evaluation interface.",
  },
  {
    question: "Is COLLE multilingual?",
    answer: "No, COLLE is available only in French. The benchmark is specifically designed to evaluate NLU models in the French language.",
  },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(null);

  const toggle = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        Frequently Asked Questions
      </h2>

      <div className="space-y-4">
        {faqs.map((faq, i) => (
          <div
            key={i}
            className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm transition"
          >
            <button
              className="w-full text-left text-xl font-semibold text-gray-800 flex justify-between items-center"
              onClick={() => toggle(i)}
            >
              <span>{`${i + 1}. ${faq.question}`}</span>
              <span className="text-2xl text-gray-500">
                {openIndex === i ? '▴' : '▾'}
              </span>
            </button>
            {openIndex === i && (
              <p className="mt-4 text-gray-600 text-sm">{faq.answer}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
