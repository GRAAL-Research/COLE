import Link from "next/link";
import CodeBlock from "../components/CodeBlock";

export default function guide() {
  return (
      <div>

        <h4>Using The Colle Benchmark</h4>

        The Colle benchmark can be used for training and/or test models on multiple tasks.
        To train or finetune a model, you should first fetch the data on HuggingFace, we recommend using HuggingFace's libraries to ease the process.
        To test, you must also fetch the data in the same way. Once that's done, you must infer answers for every line in the test split. By downloading our repository you will be able to use
        our Benchmarks for every dataset, only needing to add you own way of inferring data. If you choose to infer by yourself, you will need to format the data as explained in the next section
        before sending it our way.

        <h4 className="header">Formatting the dataset</h4>

        Before sending your results through our interface, please ensure you format your data so that our systems can treat it.
        Your results should be in the form of a JSON dictionnary like below.

        <CodeBlock>{'{tested_model_name : {benchmark : {row_number : inferred_label} }}'}</CodeBlock>
    </div>
  );
}