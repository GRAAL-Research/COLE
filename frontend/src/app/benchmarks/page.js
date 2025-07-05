import Link from 'next/link';

export default function benchmarks() {
    return (
        <div>
            <div className="max-w-3xl mx-auto px-2 py-3">
                <p className="text-1.5xl  text-left text-gray-800 ">
                    Colle is constitued of X tasks, each of them aims to test 1 or more facet of language understanding
                    in machine learning. Below are each of the tasks in more detail.
                </p>

            </div>
            <div className="space-y-8">

                <Benchmark title="Allo-ciné.ca"
                           link="https://huggingface.co/datasets/CATIE-AQ/allocine_fr_prompt_sentiment_analysis"
                           description="Allo-ciné tests language understanding in sentiment classification
            by feeding movie reviews which can be either positive and negatve, the task consists
            in giving the correct sentiment for each review.
            "
                           metrics="Accuracy"></Benchmark>

                <Benchmark title="FQuAD - French Question Answering Dataset"
                           link="https://arxiv.org/pdf/2002.06071"
                           description="Fquad is question/answer pair built on high-quality wikipedia articles. The goal of the model in this task is to accurately predict if the answer to the
            question really can be found in the provided answer."
                           metrics="F1 Score, Exact Match Ratio"></Benchmark>

                <Benchmark title="GQNLI-Fr - The Generalized Quantifier NLI Challenge Dataset"
                           link="https://huggingface.co/datasets/maximoss/gqnli-fr"
                           description="The dataset consists of carefully constructed premise-hypothesis pairs that involve quantifier logic (e.g., most, at least, more than half). The goal is to evaluate the model's ability to reason about these expressions and determine whether the hypothesis logically follows from the premise, contradicts it, or is neutral."
                           metrics="Accuracy"></Benchmark>

                <Benchmark title="Opus Parcus - Open Subtitles Paraphrase Corpus"
                           link="https://huggingface.co/datasets/GEM/opusparcus"
                           description="Opus Parcus, built with data from Open Subtitles, consists of pairs of sentences with a similar or quasi identical semantic meaning. When testing, a label is provided
            being a score of 1 to 5, with 1 meaning 2 sentences bearing no semantic similarity, and 5, 2 sentences that mean the same thing exactly."
                           metrics="Pearson"></Benchmark>

                <Benchmark title="PAWS: Paraphrase Adversaries from Word Scrambling"
                           link="https://github.com/google-research-datasets/paws"
                           description="This task aims to test paraphrase identification by giving two sentences and a label defining if these sentences are equivalent in meaning or not."
                           metrics="Accuracy"></Benchmark>

                <Benchmark title="PIAF - The French-Language Dataset of Questions-Answers"
                           link="https://aclanthology.org/2020.lrec-1.673/"
                           description="This task consists of pairs of questions and text answers with information of where in the answer is the truly relevant information."
                           metrics="F1 Score, Exact Match Ratio"></Benchmark>

                <Benchmark title="QFrCoLA - a Quebec-French Corpus of Linguistic Acceptability Judgments"
                           link="https://github.com/davebulaval/qfrcola"
                           description="QFrCoLA  is a french dataset made from multiple french language sites such as académie-française.fr and vitrinelinguistique.com.
                   It aims to tests models ability to determine a sentence's acceptability in french on subjects such as grammar and syntax. The answer is a binary label
                   indicating if the sentence is correct or not."
                           metrics="Accuracy"></Benchmark>

                <Benchmark title="QFrBLiMP - a Quebec-French Linguistic minimal pairs"
                           link="https://github.com/davebulaval/FrBLiMP"
                           description="This task gives the model sentences pairs, the goal is to determine if the sentences
            are semantically equivalent, or, put more simply, if they mean the same thing, even with slightly different
            syntax and words."
                           metrics="Accuracy"></Benchmark>

                <Benchmark title="Sick-FR - French Sentences Involving Compositional Knowledge"
                           link=" https://huggingface.co/datasets/Lajavaness/SICK-fr"
                           description="This task also has pairs of sentences and notes them on 2 dimensions, relatedness and entailment. https://paperswithcode.com/dataset/sick, While relatedness scales from 1 to 5,
            entailement is a choice between entails, contradicts or neutral."
                           metrics="Pearson"></Benchmark>

                <Benchmark title="Sts22-Crosslingual - Multilingual News Article Similarity"
                           link="https://huggingface.co/datasets/mteb/sts22-crosslingual-sts/viewer/fr"
                           description="This task evaluates whether pairs of news articles, written in different languages, cover the same story. It focuses on document-level similarity,
                where systems rate article pairs on a 4-point scale from most to least similar"
                           metrics="Pearson"></Benchmark>

                <Benchmark title="XNLI - The Cross-Lingual NLI Corpus"
                           link="https://github.com/facebookresearch/XNLI"
                           description="This task consists of pairs of sentences where the goal is to determine the relation between the two sentences, this relation can be either
                            entailement, neutral or contradiction."
                           metrics="Accuracy"></Benchmark>


            </div>


        </div>

    );
};

function Benchmark({title, description, metrics, link}) {
    return (
        <div className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <h3 className="text-xl font-semibold text-blue-700 mb-2 border-b-2 border-blue-500 inline-block">
                {link ? (
                    <Link href={link} className="hover:underline">
                        {title}
                    </Link>
                ) : (
                    title
                )}
            </h3>
            <p className="text-gray-700 mb-2">{description}</p>
            <p className="text-sm text-gray-500">
                <span className="font-medium">Metrics:</span> {metrics}
            </p>
        </div>
    );
}
