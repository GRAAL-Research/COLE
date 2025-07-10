from src.dataset.dataset import Dataset
from src.dataset.prompt_builder import PromptBuilder
from src.task import COLLE_REPOSITORY_NAME

datasets = {
    "allocine": Dataset(
        "allocine",
        "desc",
        ["0", "1"],
        COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise("Cette phrase possède-t-elle un sentiment positif ou négatif ?")
        .add_data(line["review"])
        .add_end(
            (
                "Réponds "
                "uniquement par 1 si la phrase est positive,réponds par 0 sinon. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: line["review"],
    ),
    "qfrcola": Dataset(
        "qfrcola",
        "desc",
        ["0", "1"],
        COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise("Juge si cette phrase est grammaticalement correcte :")
        .add_data(line["sentence"])
        .add_end(
            (
                "Réponds avec seulement 1 si la phrase est grammaticalement correcte, 0 sinon."
            )
        )
        .build(),
        line_to_data_fn=lambda line: line["sentence"],

    ),
    "qfrblimp": Dataset(
        "qfrblimp",
        "desc",
        ["0", "1"],
        COLLE_REPOSITORY_NAME,
        # label renvoyé comme chaîne
        line_to_thruth_fn=lambda line: str(line["label"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise("Cette phrase est-elle grammaticalement correcte ?")
        .add_data(
             {line["ungrammatical"],["grammatical"]}
        )
        .add_end(
            "Réponds avec seulement 1 si la phrase est grammaticalement correcte, 0 sinon."
        )
        .build(),
        line_to_data_fn=lambda line: {["ungrammatical"],["grammatical"]
        },
    ),

    "gqnli": Dataset(
        "gqnli",
        "desc",
        ["0", "1", "2"],
        COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Quelle est la relation de la deuxième phrase par rapport à la première ?"
        )
        .add_data(line["premise"])
        .add_data(line["hypothesis"])
        .add_end(
            (
                "Réponds uniquement par :\n"
                "0 — si la deuxième phrase implique la première,\n"
                "1 — si la relation est neutre,\n"
                "2 — s'il y a contradiction.\n"
                "Réponds uniquement par 0, 1 ou 2."
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "premise": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
    "opus_parcus": Dataset(
        "opus_parcus",
        "desc",
        [str(i) for i in range(0, 101, 5)],
        COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["quality"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Les deux phrases suivantes expriment-elles la même idée ou sont-elles différentes ?"
        )
        .add_data(line["sent1"])
        .add_data(line["sent2"])
        .add_end(
            (
                "Réponds seulement avec un chiffre entre 60 et 100 où 100"
                " signifie que les deux phrases veulent dire exactement la même chose."
            )
        )
        .build(),
        line_to_data_fn=lambda line: {"sent1": line["sent1"], "sent2": line["sent2"]},
    ),
    "paws_x": Dataset(
        "paws_x",
        "desc",
        ["0", "1"],
        COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Les deux phrases suivantes veulent-elles dire la même chose, ou ont-elles des significations différentes ?"
        )
        .add_data(line["sentence1"])
        .add_data(line["sentence1"])
        .add_end(
            (
                "Réponds seulement 1 si les deux phrases ont la même signification, 0 sinon. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "sentence1 ": line["sentence1"],
            "sentence2 ": line["sentence2"],
        },
    ),
    "piaf": Dataset(
    "piaf",
    "desc",
    [],
    COLLE_REPOSITORY_NAME,

        line_to_thruth_fn=lambda line:
            line["answers"],


    line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Tu vas recevoir un contexte et une question.\n"
            "→ Donne **exactement** le passage du contexte qui répond à la question.\n"
            "→ Immédiatement après, mets trois barres verticales `|||` puis le nombre de caractères qui le précèdent.\n"
        )
        .add_data(f"Contexte  : {line['context']}")
        .add_data(f"Question : {line['question']}")
        .add_end("Réponse :")
        .build(),

    line_to_data_fn=lambda line: {
        "context":  line["context"],
        "question": line["question"],
    },
),
    "fquad": Dataset(
    "fquad",
    "desc",

    [],
    COLLE_REPOSITORY_NAME,
    line_to_thruth_fn=lambda line:
         line["answers"],

    line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Tu vas recevoir un contexte et une question.\n"
            "→ Donne **exactement** le passage du contexte qui répond à la question.\n"
            "→ Immédiatement après, mets trois barres verticales `|||` puis le nombre de caractères qui le précèdent.\n"

        )
        .add_data(f"Contexte  : {line['context']}")
        .add_data(f"Question : {line['question']}")
        .add_end("Réponse :")
        .build(),
    line_to_data_fn=lambda line: {
        "context":  line["context"],
        "question": line["question"],
    },
),

    "sickfr": Dataset(
        "sickfr",
        "desc",
        [i * 0.1 for i in range(0, 51)],
        COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: float(line["relatedness_score"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "À quel point, de 0 à 5, les 2 phrases suivantes sont-elles similaires ?"
        )
        .add_data(
            f"sentence_A : {line['sentence_A']}\n" f"sentence_B: {line['sentence_B']}"
        )
        .add_end(
            (
                "Réponds avec seulement un nombre de 0 à 5, où 5 signifie une très grande similarité entre les phrases."
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "sentence_A ": line["sentence_A"],
            "sentence_B ": line["sentence_B"],
        },
    ),
    "sts22": Dataset(
        "sts22",
        "desc",
        [i * 0.1 for i in range(0, 51)],
        COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: float(line["score"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "En scorant de 0 à 5, à quel point les phrases suivants sont-elles similaires ?"
        )
        .add_data(
            f"sentence 1: {line['sentence1']}\n" f"sentence 2: {line['sentence2']}"
        )
        .add_end(
            (
                "Réponds seulement avec un nombre de 0 à 5, où 5 signifie que les 2 phrases veulent dire exactement la même chose. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "sentence 1 ": line["sentence1"],
            "sentence 2 ": line["sentence2"],
        },
    ),
    "xnli": Dataset(
        "xnli",
        "desc",
        ["0", "1", "2"],
        COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: str(line["label"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Quelle est la relation de la deuxième phrase par rapport à la première ?"
        )
        .add_data(
            f"premise    : {line['premise']}\n" f"sentence 2: {line['hypothesis']}"
        )
        .add_end(
            (
                "Réponds uniquement par :\n"
                "0 — si la deuxième phrase implique la première,\n"
                "1 — si la relation est neutre,\n"
                "2 — s'il y a contradiction.\n"
                "Réponds uniquement par 0, 1 ou 2."
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "premise ": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
}
