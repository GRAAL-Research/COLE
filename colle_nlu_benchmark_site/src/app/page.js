import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div>Colle is a multidisciplinar french Natural Language Understanding benchmark(<a href="https://en.wikipedia.org/wiki/Natural_language_understanding">NLU</a>).
    It takes inspiration from its predecessors <a href="https://gluebenchmark.com/">GLUE</a> and <a href="https://super.gluebenchmark.com/">SuperGLUE</a>  to build a benchmark capable of evaluating
    models in the french language on multiple topics of language understanding, see <a href="404.html">our paper</a> for more information.
    
    The Colle benchmark is built with multiple goals in mind. First, it aims to provide a solid and complete french alternative for benchmarking models on
    NLU tasks. Second, it provides the user with multiple datasets, all usable through the HuggingFace's libraries, to train or finetune models on the specific tasks.

    We have made the choice to hide test labels to discourage cheating or overfitting on test data. To get results on your test data, you may send us your results as explained in <a href="guide.html">our guide</a>
    </div>
  );
}
