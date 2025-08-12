from src.dataset.dataset import Dataset
from src.dataset.prompt_builder import PromptBuilder
from src.task import COLE_REPOSITORY_NAME
from src.task.task_names import Tasks

datasets = {
    Tasks.ALLOCINE.value: Dataset(
        name=Tasks.ALLOCINE.value,
        description="Binary classification on sentiment analysis"
        " of movie reviews, with reviews being either positive (1) or negative (0).",
        possible_ground_truths=["0", "1"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise("Cette phrase possède-t-elle un sentiment positif ou négatif ?")
        .add_data(line["review"])
        .add_end(
            (
                "Réponds "
                "uniquement par 1 si la phrase est positive, réponds par 0 sinon. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: line["review"],
    ),
    Tasks.QFRCOLA.value: Dataset(
        name=Tasks.QFRCOLA.value,
        description="Binary grammatical judgement : "
        "Predicts whether a sentence is grammatically correct (1) or not. (0)",
        possible_ground_truths=["0", "1"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise("Juge si cette phrase est grammaticalement correcte :")
        .add_data(line["sentence"])
        .add_end(
            (
                "Réponds avec seulement 1 si la phrase est grammaticalement correcte, 0 sinon. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: line["sentence"],
    ),
    Tasks.QFRBLIMP.value: Dataset(
        name=Tasks.QFRBLIMP.value,
        description="Choice task between two sentences : Choose the one which is grammatically correct.",
        possible_ground_truths=["0", "1"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(
            line["label"]
        ),  # The label is return as a string.
        line_to_prompt_fn=lambda line: (
            PromptBuilder()
            .add_premise("Laquelle de ces phrases est grammaticalement correcte ?")
            .add_data(f"Phrase 0:{line['sentence_a']}")
            .add_data(f"Phrase 1:{line['sentence_b']}")
            .add_end(
                "Réponds avec seulement 0 si la phrase 0 "
                "est grammaticalement correcte, et uniquement 1 si la phrase 1 est grammaticalement "
                "correcte. La réponse est :"
            )
            .build()
        ),
        line_to_data_fn=lambda line: {line["sentence_a"], line["sentence_b"]},
    ),
    Tasks.GQNLI.value: Dataset(
        name=Tasks.GQNLI.value,
        description="Natural language inference task : "
        "predict the relation between two sentences (implication, neutral, contradiction)",
        possible_ground_truths=["0", "1", "2"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Quelle est la relation de la deuxième phrase par rapport à la première ?"
        )
        .add_data(line["premise"])
        .add_data(line["hypothesis"])
        .add_end(
            (
                r"Réponds uniquement par :\n"
                r"0 - si la deuxième phrase implique la première,\n"
                r"1 - si la relation est neutre,\n"
                r"2 - s'il y a contradiction.\n"
                "Réponds uniquement par 0, 1 ou 2. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "premise": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
    Tasks.SICKFR.value: Dataset(
        name=Tasks.SICKFR.value,
        description="Natural language inference task : "
        "predict the relation between two sentences (implication, neutral, contradiction)",
        possible_ground_truths=["0", "1", "2"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["label"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise("Détermine la relation entre les deux phrases suivantes :")
        .add_data(f"Phrase A : {line['sentence_A']}\nPhrase B : {line['sentence_B']}")
        .add_end(
            "Réponds uniquement par un chiffre :\n"
            "0 - si la deuxième phrase découle logiquement de la première,\n"
            "1 - si leur relation est neutre,\n"
            "2 - si les phrases se contredisent.\n"
            "La réponse est :"
        )
        .build(),
        line_to_data_fn=lambda line: {
            "sentence_A": line["sentence_A"],
            "sentence_B": line["sentence_B"],
        },
    ),
    Tasks.STS22.value: Dataset(
        name=Tasks.STS22.value,
        description="Semantic textual similarity task : "
        "Predict how similar two sentences are to each other (1 to 4)",
        possible_ground_truths=["1", "2", "3", "4"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["score"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "À quel point les deux phrases suivantes sont-elles similaires ? Donne une note entière de 1 à 4."
        )
        .add_data(f"Phrase 1 : {line['sentence1']}\nPhrase 2 : {line['sentence2']}")
        .add_end(
            "Réponds uniquement avec un nombre entier entre 1 (aucune similarité) et 4 (équivalence parfaite). "
            "La réponse est :"
        )
        .build(),
        line_to_data_fn=lambda line: {
            "sentence1": line["sentence1"],
            "sentence2": line["sentence2"],
        },
    ),
    Tasks.PAWS_X.value: Dataset(
        name=Tasks.PAWS_X.value,
        description="Binary classification task : "
        "Predict if two sentences have the same meaning (1) or not (0)",
        possible_ground_truths=["0", "1"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Les deux phrases suivantes veulent-elles dire la même chose, ou ont-elles des significations différentes ?"
        )
        .add_data(line["sentence1"])
        .add_data(line["sentence2"])
        .add_end(
            (
                "Réponds seulement 1 si les deux phrases ont la même signification, 0 sinon. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "sentence1": line["sentence1"],
            "sentence2": line["sentence2"],
        },
    ),
    Tasks.PIAF.value: Dataset(
        name=Tasks.PIAF.value,
        description="Extractive question answering task : Extract a question's answer from a given context.",
        possible_ground_truths=[],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["answers"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Tu vas recevoir un contexte suivi d'une question.\n"
            "Ta tâche est d'extraire **mot pour mot** le passage du contexte qui répond le mieux à la question.\n"
            "N'invente rien. Ne reformule pas.\n"
            "Réponds **en copiant uniquement** un extrait exact du texte ci-dessus."
        )
        .add_data(f"Contexte  : {line['context']}")
        .add_data(f"Question : {line['question']}")
        .add_end(
            "Réponds uniquement par un passage extrait du contexte. La réponse est :"
        )
        .build(),
        line_to_data_fn=lambda line: {
            "context": line["context"],
            "question": line["question"],
        },
    ),
    Tasks.FQUAD.value: Dataset(
        name=Tasks.FQUAD.value,
        description="Extractive question answering task : Extract a question's answer from a given context.",
        possible_ground_truths=[],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["answers"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Tu vas recevoir un contexte suivi d'une question.\n"
            "Ta tâche est d'extraire **mot pour mot** le passage du contexte qui répond le mieux à la question.\n"
            "N'invente rien. Ne reformule pas.\n"
            "Réponds **en copiant uniquement** un extrait exact du texte ci-dessus."
        )
        .add_data(f"Contexte  : {line['context']}")
        .add_data(f"Question : {line['question']}")
        .add_end(
            "Réponds uniquement par un passage extrait du contexte. La réponse est :"
        )
        .build(),
        line_to_data_fn=lambda line: {
            "context": line["context"],
            "question": line["question"],
        },
    ),
    Tasks.XNLI.value: Dataset(
        name=Tasks.XNLI.value,
        description="Natural language inference task : "
        "predict the relation between two sentences (implication, neutral, contradiction)",
        possible_ground_truths=["0", "1", "2"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["label"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Quelle est la relation de la deuxième phrase par rapport à la première ?"
        )
        .add_data(rf"premise : {line['premise']}\n" f"sentence 2: {line['hypothesis']}")
        .add_end(
            (
                r"Réponds uniquement par :\n"
                r"0 - si la deuxième phrase implique la première,\n"
                r"1 - si la relation est neutre,\n"
                r"2 - s'il y a contradiction.\n"
                r"Réponds uniquement par 0, 1 ou 2. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "premise": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
    Tasks.QFRCORE.value: Dataset(
        name=Tasks.QFRCORE.value,
        description="Definition matching task : "
        "Match the Quebec expression with its definition from a list",
        possible_ground_truths=[str(i) for i in range(10)],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["correct_index"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            f"Que veut dire cette expression québécoise « {line['expression']} » ?"
        )
        .add_data(
            "\n".join(
                f"{idx} - {definition}"
                for idx, definition in enumerate(line["choices"])
            )
        )
        .add_end(
            (
                "Réponds uniquement par l'index, débutant à zéro,  "
                "de la bonne définition parmi la liste ci-dessus. Par exemple, si la "
                "troisième phrase correspond à l'expression, la réponse sera 2. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "expression": line["expression"],
            "choices": line["choices"],
        },
    ),
    Tasks.QFRCORT.value: Dataset(
        name=Tasks.QFRCORT.value,
        description="Definition matching task : "
        "Match the Quebec term with its definition from a list",
        possible_ground_truths=[str(i) for i in range(10)],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["correct_index"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            f"Qu'est-ce que ça veut dire ce terme québécois « {line['terme']} » ?"
        )
        .add_data(
            "\n".join(
                f"{idx} - {definition}"
                for idx, definition in enumerate(line["choices"])
            )
        )
        .add_end(
            (
                "Réponds uniquement par l'index, débutant à zéro,  "
                "de la bonne définition parmi la liste ci-dessus. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "terme": line["terme"],
            "choices": line["choices"],
        },
    ),
    Tasks.DACCORD.value: Dataset(
        name=Tasks.DACCORD.value,
        description="Paraphrase detection task :"
        "Predict whether the two sentences are compatible (0) "
        "or contradict each other (1).",
        possible_ground_truths=["0", "1"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["label"]),
        line_to_prompt_fn=lambda line: (
            PromptBuilder()
            .add_premise("Détermine la relation entre les deux phrases suivantes :")
            .add_data(f"Première phrase : {line['premise']}")
            .add_data(f"Deuxième phrase : {line['hypothesis']}")
            .add_end(
                "Réponds uniquement par :\n"
                "0 - si les deux phrases sont compatibles (elles expriment la même information ou sont cohérentes),\n"
                "1 - s'il y a contradiction entre les deux phrases.\n"
                "Réponds uniquement par 0 ou 1. La réponse est :"
            )
            .build()
        ),
        line_to_data_fn=lambda line: {
            "premise": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
    Tasks.FRENCH_BOOLQ.value: Dataset(
        name=Tasks.FRENCH_BOOLQ.value,
        description="Binary question answering task : "
        "Answer whether the context allows answering 'yes' to the question (1)"
        "or, if the context only allows answering 'no' "
        "to the question or does not answer the question. (0)",
        possible_ground_truths=["0", "1"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["label"]),
        line_to_prompt_fn=lambda line: (
            PromptBuilder()
            .add_premise(
                "Lis le passage suivant et réponds à la question en te basant uniquement sur le texte :\n"
                "- Si le passage permet d'affirmer que la réponse à la question est oui, réponds 1.\n"
                "- Sinon, si la réponse est non ou que le passage ne permet pas de répondre à la question, réponds 0."
            )
            .add_data(f"Passage : {line['passage']}")
            .add_data(f"Question : {line['question']}")
            .add_end("La réponse est :")
            .build()
        ),
        line_to_data_fn=lambda line: {
            "question": line["question"],
            "passage": line["passage"],
        },
    ),
    Tasks.MNLI_NINEELEVEN_FR_MT.value: Dataset(
        name=Tasks.MNLI_NINEELEVEN_FR_MT.value,
        description="Natural language inference task : "
        "predict the relation between two sentences (implication, neutral, contradiction)",
        possible_ground_truths=["0", "1", "2"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Quelle est la relation de la deuxième phrase par rapport à la première ?"
        )
        .add_data(line["premise"])
        .add_data(line["hypothesis"])
        .add_end(
            (
                r"Réponds uniquement par :\n"
                r"0 - si la deuxième phrase implique la première,\n"
                r"1 - si la relation est neutre,\n"
                r"2 - s'il y a contradiction.\n"
                "Réponds uniquement par 0, 1 ou 2. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "premise": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
    Tasks.RTE3_FRENCH.value: Dataset(
        name=Tasks.RTE3_FRENCH.value,
        description="Natural language inference task : "
        "predict the relation between two sentences (implication, neutral, contradiction)",
        possible_ground_truths=["0", "1", "2"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["label"]),
        line_to_prompt_fn=lambda line: (
            PromptBuilder()
            .add_premise(
                "Lis le texte suivant et détermine la relation de l'énoncé par rapport au texte."
            )
            .add_data(f"Texte : {line['premise']}")
            .add_data(f"Énoncé : {line['hypothesis']}")
            .add_end(
                "Réponds uniquement par :\n"
                "0 - si l'énoncé découle logiquement du texte (entailment),\n"
                "1 - si la relation est neutre,\n"
                "2 - s'il y a contradiction.\n"
                "La réponse est :"
            )
            .build()
        ),
        line_to_data_fn=lambda line: {
            "premise": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
    Tasks.WINO_X_LM.value: Dataset(
        name=Tasks.WINO_X_LM.value,
        description=(
            "Pronoun resolution task : predict the correct referent (1 or 2) "
            "of a pronoun in a sentence by choosing between two candidates."
        ),
        possible_ground_truths=["1", "2"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["answer"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Voici une phrase en anglais contenant le pronom \"it\" dans un sens ambigu et sa traduction en français."
        )
        .add_data(f"Phrase (originale en anglais) : {line['sentence']}")
        .add_data(
            f"Traduction en français (le pronom est caché par '_' ) : {line['context_fr']}"
        )
        .add_data("À quoi renvoie ce pronom ? Voici les choix: ")
        .add_data(f"1 : {line['option1_fr']}")
        .add_data(f"2 : {line['option2_fr']}")
        .add_end("Réponds uniquement par 1 ou 2. La réponse est :")
        .build(),
        line_to_data_fn=lambda line: {
            "sentence": line["sentence"],
            "translation": line["context_fr"],
            "referent1": line["option1_fr"],
            "referent2": line["option2_fr"],
        },
    ),
    Tasks.WINO_X_MT.value: Dataset(
        name="wino_x_mt",
        description=(
            "Résolution de pronom à partir de traductions : choisir entre deux traductions françaises "
            "d'une phrase anglaise avec pronom ambigu. L'objectif est d'identifier laquelle des deux "
            "traductions utilise le bon pronom (il ou elle) en fonction du référent correct."
        ),
        possible_ground_truths=["1", "2"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(line["answer"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Voici deux traductions d’une phrase anglaise contenant un pronom ambigu :"
        )
        .add_data(f"Phrase originale : {line['sentence']}")
        .add_data(f"Traduction 1 (avec '{line['pronoun1']}') : {line['translation1']}")
        .add_data(f"Traduction 2 (avec '{line['pronoun2']}') : {line['translation2']}")
        .add_end(
            "Quelle traduction utilise le bon pronom en fonction du référent visé dans la phrase originale ?\n"
            "Réponds uniquement par 1 si la traduction 1 est correcte, ou 2 si la traduction 2 est correcte.\n"
            "La réponse est :"
        )
        .build(),
        line_to_data_fn=lambda line: {
            "sentence": line["sentence"],
            "translation1": line["translation1"],
            "translation2": line["translation2"],
            "pronoun1": line["pronoun1"],
            "pronoun2": line["pronoun2"],
        },
    ),
    Tasks.MULTIBLIMP.value: Dataset(
        name=Tasks.MULTIBLIMP.value,
        description="Choice task between two sentences : Choose the one which is grammatically correct.",
        possible_ground_truths=["0", "1"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: str(
            line["label"]
        ),  # The label is return as a string.
        line_to_prompt_fn=lambda line: (
            PromptBuilder()
            .add_premise("Laquelle de ces phrases est grammaticalement correcte ?")
            .add_data(f"Phrase 0:{line['sentence_a']}")
            .add_data(f"Phrase 1:{line['sentence_b']}")
            .add_end(
                "Réponds avec seulement 0 si la phrase 0 "
                "est grammaticalement correcte, et uniquement 1 si la phrase 1 est grammaticalement "
                "correcte. La réponse est :"
            )
            .build()
        ),
        line_to_data_fn=lambda line: {line["sentence_a"], line["sentence_b"]},
    ),
    Tasks.FRACAS.value: Dataset(
        name=Tasks.FRACAS.value,
        description="Natural language inference task : "
        "predict the relation between two sentences (implication, neutral, contradiction)",
        possible_ground_truths=["0", "1", "2"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Quelle est la relation de la deuxième phrase par rapport à la première ?"
        )
        .add_data(line["premise"])
        .add_data(line["hypothesis"])
        .add_end(
            (
                r"Réponds uniquement par :\n"
                r"0 - si la deuxième phrase implique la première,\n"
                r"1 - si la relation est neutre,\n"
                r"2 - s'il y a contradiction.\n"
                "Réponds uniquement par 0, 1 ou 2. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "premise": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
    Tasks.MMS.value: Dataset(
        name=Tasks.MMS.value,
        description="A sentiment analysis task for classifying text as positive (2), negative (0), or neutral (1).",
        possible_ground_truths=["0", "1", "2"],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise("Quel est le sentiment de cette phrase?")
        .add_data(line["text"])
        .add_end(
            (
                r"Réponds uniquement par :\n"
                r"0 - si la phrase est négative,\n"
                r"1 - si la phrase est neutre,\n"
                r"2 - si la phrase est positive.\n"
                "Réponds uniquement par 0, 1 ou 2. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "text": line["text"],
        },
    ),
    Tasks.WSD.value: Dataset(
        name=Tasks.WSD.value,
        description="Extractive word sense disambiguation : Extract an ambiguous word in a sentence.",
        possible_ground_truths=[],
        hugging_face_repo=COLE_REPOSITORY_NAME,
        line_to_truth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Tu vas recevoir une phrase contenant un mot ambigu.\n"
            "Ta tâche est d’indiquer **exactement** ce mot, sans rien ajouter ni reformuler.\n"
            "Réponds uniquement avec le mot ambigu identifié."
        )
        .add_data(f"Phrase : {line['sentence']}")
        .add_end("La réponse est :")
        .build(),
        line_to_data_fn=lambda line: {
            "sentence": line["sentence"],
        },
    ),
}


def preload_all_datasets():
    """Loads all datasets into cache for later usage"""
    for dataset in datasets.values():
        dataset.load_data()


def generate_metadata_dict():
    """Generates a dictionary with all the datasets metadata information"""
    metadata_dict = {}
    for dataset in datasets.values():
        metadata_dict[dataset.name] = dataset.metadata
    return metadata_dict
