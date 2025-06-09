import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        What is Colle?
      </h2>
      <p className="text-gray-700 mb-4 leading-relaxed space-y-4">
        Colle is a multidisciplinary French Natural Language Understanding benchmark (
        <a
          href="https://en.wikipedia.org/wiki/Natural_language_understanding"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline hover:text-blue-800"
        >
          NLU
        </a>
        ). It takes inspiration from its predecessors&nbsp;
        <a
          href="https://gluebenchmark.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline hover:text-blue-800"
        >
          GLUE
        </a>{" "}
        and&nbsp;
        <a
          href="https://super.gluebenchmark.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline hover:text-blue-800"
        >
          SuperGLUE
        </a>{" "}
        to build a benchmark capable of evaluating models in the French language on multiple topics of language understanding. See&nbsp;
        <Link
          href="/404"
          className="text-blue-600 underline hover:text-blue-800"
        >
          our paper
        </Link>{" "}
        for more information.
      </p>

      <p className="text-gray-700 leading-relaxed">
        The Colle benchmark is built with multiple goals in mind. First, it aims to provide a solid and complete French alternative for benchmarking models on NLU tasks. Second, it provides the user with multiple datasets, all usable through HuggingFace’s libraries, to train or fine-tune models on specific tasks.
      </p>

      <p className="text-gray-700 leading-relaxed mt-4">
        We have made the choice to hide test labels to discourage cheating or overfitting on test data. To get results on your test data, you may send us your results as explained in&nbsp;
        <Link
          href="/guide"
          className="text-blue-600 underline hover:text-blue-800"
        >
          our guide
        </Link>
        .
      </p>
    </div>
  );
}
