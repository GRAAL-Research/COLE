export default function FAQ() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        Frequently Asked Questions
      </h2>

      <div className="space-y-8">
        <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow transition">
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Q: When will this site be completed?
          </h3>
          <p className="text-gray-600">
            A: The site is currently under development and will be released as soon as it is ready.
          </p>
        </div>

        <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow transition">
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Q: How can I evaluate my model?
          </h3>
          <p className="text-gray-600">
            A: You can upload your model outputs in JSON format on the website. The system will automatically evaluate them, and you can view the results in the evaluation interface.
          </p>
        </div>

        <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow transition">
          <h3 className="text-xl font-semibold text-gray-800 mb-2">
            Q: Is COLLE multilingual?
          </h3>
          <p className="text-gray-600">
            A: No, COLLE is currently available only in French. The benchmark is specifically designed to evaluate NLU models in the French language.
          </p>
        </div>
      </div>
    </div>
  );
}
