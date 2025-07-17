import Link from "next/link";
import CodeBlock from "../components/CodeBlock";

export default function Contact() {
  return (
      <div className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        Contact us
      </h2>

        <p className="text-gray-700 mb-4 leading-relaxed">
          If you have any questions, feedback, or suggestions regarding the COLLE benchmark, feel free to reach out to us.
          We are happy to help — please note that response times may vary.
        </p>

        <div className="bg-gray-50 p-4 rounded-md border border-dashed border-blue-400">
          <p className="text-sm text-gray-500 mb-2">Email us at:</p>
          <a
            href="mailto:david.beauchemin@ift.ulaval.ca"
            className="text-blue-600 font-mono text-lg hover:underline"
          >
            david.beauchemin@ift.ulaval.ca
          </a>
        </div>
    </div>
  );
}
