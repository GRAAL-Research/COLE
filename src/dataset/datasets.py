from src.dataset.Dataset import Dataset
from src.dataset.prompt_builder import PromptBuilder
from src.task import COLLE_REPOSITORY_NAME

datasets = {
    "qfrcola ": Dataset(
        "qfrcola",
        "desc",
        "[0,1]",
        COLLE_REPOSITORY_NAME,
        line_to_thruth_fn=lambda line: PromptBuilder()
        .add_premise("Cette phrase possède-t-elle un sentiment positif ou négatif ?")
        .add_data(line["review"])
        .add_end(
            (
                "Réponds "
                "uniquement par 1 si la phrase est positive,réponds par 0 sinon. La réponse est : "
            )
        )
        .build(),
        line_to_prompt_fn=lambda line: line["label"],
        line_to_data_fn=lambda line: line["review"],
    )
}
