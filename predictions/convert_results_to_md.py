import json
from pathlib import Path
from tabulate import tabulate

RESULTS_DIRECTORY = "../results"


def results_data(results_dir=RESULTS_DIRECTORY):
    datas = []
    directory = Path(results_dir)
    file_path_list = [f for f in directory.rglob("*metrics.json") if f.is_file()]
    for file_path in file_path_list:
        with open(file_path, "r", encoding="utf-8") as file:
            datas.append(json.load(file))
    return datas


def format_as_small_rows():
    headers = ["Model", "Task", "Metric", "Results"]
    rows = []
    for data in results_data():
        model_name = data["model_name"]
        for task in data["tasks"]:
            for task_name, metrics_values in task.items():
                for metric_name, metric_values in metrics_values.items():
                    formatted_metrics = "||".join(
                        [
                            f"{key}:{value:.4f}"
                            for key, value in metric_values.items()
                            if isinstance(value, (int, float))
                        ]
                    )
                    rows.append([model_name, task_name, metric_name, formatted_metrics])
    markdown_tb = tabulate(rows, headers=headers, tablefmt="github")
    return markdown_tb
