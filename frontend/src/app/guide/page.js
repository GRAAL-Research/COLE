import Link from "next/link";
import CodeBlock from "../components/CodeBlock";

export default function Guide() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        Using the COLLE Benchmark
      </h2>

      <div className="space-y-8">
        <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow transition">
          <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-4">
              Training and Testing
          </h3>

          <p className="text-gray-700">
            The COLLE benchmark can be used to train and/or test models on multiple tasks. To train or fine-tune a model, you can fetch the train, validation and test data splits from our <a
          href="https://huggingface.co/datasets/graalul/COLLE-public"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline hover:text-blue-800"
        >
          Hugging Face public repository
        </a>. We recommend using Hugging Face’s libraries to simplify the process.
          </p>
          <p className="text-gray-700 mt-4">
            To test a model, you also need to fetch the data in the same way. Once done, your model should infer predictions for each line in the test split. Our repository includes benchmark evaluation scripts for each dataset. You only need to plug in your model's inference method using HuggingFace Model interface. Our inference script are available on our <a
          href="https://github.com/GRAAL-Research/colle"
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline hover:text-blue-800">
            GitHub Repository
          </a>.
          </p>
          <p className="text-gray-700 mt-4">
            If you prefer to run inference separately, please ensure that the predictions are formatted correctly before submitting them for evaluation (see our "Formatting the Dataset" section).
          </p>

          <h3 className="text-2xl font-semibold text-gray-900 mb-4 border-l-4 border-blue-600 pl-4">
            Formatting the Dataset
          </h3>
          <p className="text-gray-700 mb-4">
            Before submitting your results, make sure your output is properly formatted so that our systems can process it. The expected format is a nested JSON dictionary as follows:
          </p>

          <CodeBlock>
            {`{
  "model_name": "a_model_name",
  "model_url": "a_model_url",
  "tasks": [
      {
          "qfrcola": {
              "predictions": [1, 1, 1, 1, 1]
          }
      },
      {
          "allocine": {
              "predictions": [1, 1, 1, 1, 1]
          }
      }
  ]
}`}
          </CodeBlock>
        </div>
      </div>
    </div>
  );
}
