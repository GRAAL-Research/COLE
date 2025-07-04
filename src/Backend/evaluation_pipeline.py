from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.abstract_model import LightevalModel
from lighteval.pipeline import Pipeline, PipelineParameters


def evaluation_submission(
    task_str: str,
    results_tracker: EvaluationTracker,
    pipeline_parameters: PipelineParameters,
    model: LightevalModel,
):
    pipeline = Pipeline(
        tasks=task_str,
        pipeline_parameters=pipeline_parameters,
        evaluation_tracker=results_tracker,
        model=model,
    )

    pipeline.evaluate()
