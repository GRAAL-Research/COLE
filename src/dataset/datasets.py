from src.dataset.dataset import Dataset
from src.dataset.prompt_builder import PromptBuilder
from src.task import COLLE_REPOSITORY_NAME

datasets = {
    "allocine": Dataset(
        name="allocine",
        description="desc",
        possible_ground_thruths=["0", "1"],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["label"],
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
    "qfrcola": Dataset(
        name="qfrcola",
        description="desc",
        possible_ground_thruths=["0", "1"],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["label"],
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
    "qfrblimp": Dataset(
        name="qfrblimp",
        description="desc",
        possible_ground_thruths=["0", "1"],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: str(line["label"]),  # The label is return as a string.
        line_to_prompt_fn=lambda line: (
            PromptBuilder()
            .add_premise("Laquelle de ces phrases est grammaticalement correcte ?")
            .add_data(f"Phrase 0:{line['sentence_a']}")
            .add_data(f"Phrase 1:{line['sentence_b']}")
            .add_end(
                "Réponds avec seulement 0 si la phrase 0 "
                "est grammaticalement correcte, et uniquement 1 si la phrase 1 est grammaticalement correcte. La réponse est :"
            )
            .build()
        ),
        line_to_data_fn=lambda line: {line["sentence_a"], line["sentence_b"]},
    ),
    "gqnli": Dataset(
        name="gqnli",
        description="desc",
        possible_ground_thruths=["0", "1", "2"],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["label"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Quelle est la relation de la deuxième phrase par rapport à la première ?"
        )
        .add_data(line["premise"])
        .add_data(line["hypothesis"])
        .add_end(
            (
                r"Réponds uniquement par :\n"
                r"0 — si la deuxième phrase implique la première,\n"
                r"1 — si la relation est neutre,\n"
                r"2 — s'il y a contradiction.\n"
                "Réponds uniquement par 0, 1 ou 2. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "premise": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
    "opus_parcus": Dataset(
        name="opus_parcus",
        description="desc",
        possible_ground_thruths=[str(i) for i in range(0, 101, 5)],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
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
                " signifie que les deux phrases veulent dire exactement la même chose. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {"sent1": line["sent1"], "sent2": line["sent2"]},
    ),
    "paws_x": Dataset(
        name="paws_x",
        description="desc",
        possible_ground_thruths=["0", "1"],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
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
        name="piaf",
        description="desc",
        possible_ground_thruths=[],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["answers"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Tu vas recevoir un contexte et une question. "
            "Donne exactement le passage du contexte qui répond à la question. La réponse est :"
        )
        .add_data(f"Contexte  : {line['context']}")
        .add_data(f"Question : {line['question']}")
        .add_end("Réponse :")
        .build(),
        line_to_data_fn=lambda line: {
            "context": line["context"],
            "question": line["question"],
        },
    ),
    "fquad": Dataset(
        name="fquad",
        description="desc",
        possible_ground_thruths=[],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: line["answers"],
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Tu vas recevoir un contexte et une question. "
            "Donne exactement le passage du contexte qui répond à la question. La réponse est :"
        )
        .add_data(f"Contexte  : {line['context']}")
        .add_data(f"Question : {line['question']}")
        .add_end("Réponse :")
        .build(),
        line_to_data_fn=lambda line: {
            "context": line["context"],
            "question": line["question"],
        },
    ),
    "sickfr": Dataset(
        name="sickfr",
        description="desc",
        possible_ground_thruths=[i * 0.1 for i in range(0, 51)],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
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
                "Réponds avec seulement un nombre de 0 à 5, où 5 signifie une très grande similarité entre "
                "les phrases et 0 aucune similarité entre les phrases. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "sentence_A ": line["sentence_A"],
            "sentence_B ": line["sentence_B"],
        },
    ),
    "sts22": Dataset(
        name="sts22",
        description="desc",
        possible_ground_thruths=[i * 0.1 for i in range(0, 51)],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: float(line["score"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "À quel point, de 0 à 5, les 2 phrases suivantes sont-elles similaires ?"
        )
        .add_data(
            f"sentence 1: {line['sentence1']}\n" f"sentence 2: {line['sentence2']}"
        )
        .add_end(
            (
                "Réponds seulement avec un nombre de 0 à 5, "
                "où 5 signifie que les 2 phrases veulent dire exactement la même chose et 0 qu'elles ne veulent "
                "pas dire la même chose. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "sentence 1 ": line["sentence1"],
            "sentence 2 ": line["sentence2"],
        },
    ),
    "xnli": Dataset(
        name="xnli",
        description="desc",
        possible_ground_thruths=["0", "1", "2"],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: str(line["label"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            "Quelle est la relation de la deuxième phrase par rapport à la première ?"
        )
        .add_data(
            fr"premise : {line['premise']}\n" f"sentence 2: {line['hypothesis']}"
        )
        .add_end(
            (
                r"Réponds uniquement par :\n"
                r"0 — si la deuxième phrase implique la première,\n"
                r"1 — si la relation est neutre,\n"
                r"2 — s'il y a contradiction.\n"
                r"Réponds uniquement par 0, 1 ou 2. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "premise ": line["premise"],
            "hypothesis": line["hypothesis"],
        },
    ),
    "expressions_quebecoises": Dataset(
        name="expressions_quebecoises",
        description="desc",
        possible_ground_thruths=[str(i) for i in range(11)],
        hugging_face_repo=COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: str(line["correct_index"]),
        line_to_prompt_fn=lambda line: PromptBuilder()
        .add_premise(
            f"Qu'est-ce que ça veut dire cette expression québécoise « {line['expression']} » ?"
        )
        .add_data(
            "\n".join(
                f"{idx} — {definition}"
                for idx, definition in enumerate(line["choices"])
            )
        )
        .add_end(
            (
                "Réponds uniquement par l'index, débutant à zéro,  "
                "de la bonne définition parmi la liste ci-dessus. Par exemple, si c'est la "
                "troisième phrase, la réponse sera 2. La réponse est :"
            )
        )
        .build(),
        line_to_data_fn=lambda line: {
            "expression": line["expression"],
            "choices": line["choices"],
        },
    ),
}


def preload_all_datasets():
    for dataset in datasets.values():
        dataset.load_data()
