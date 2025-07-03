import json
from pathlib import Path
from tabulate import tabulate


RESULTS_DIRECTORY = "./results"


def results_data(results_dir = RESULTS_DIRECTORY ):
    datas = []
    directory = Path(RESULTS_DIRECTORY)
    file_path_list = [f for f in directory.rglob('*.json') if f.is_file()]
    for file_path in file_path_list:
        with open(file_path) as file:
            datas.append(json.load(file))
    return datas
def format_as_wide_rows():
    headers = ["Model", "Task", "Results"]
    rows = []
    known_datasets = []
    for data in results_data():
        print(data)
        row = ["NaN"] * len(known_datasets)
        for key, value in data["results"].items():
            formatted_metrics = [f"{key}:{value:.4f}" for key, value in value.items()]

            value = "<br>".join(formatted_metrics)
            if key in known_datasets:
                row[known_datasets.index(key)] = value
            else:
                known_datasets.append(key)
                row.append(value)
        row.insert(0, data["config_general"]["model_name"])
        rows.append(row)
    headers = ["Model"]
    headers.extend(known_datasets)
    markdown_tb = tabulate(rows, headers=headers, tablefmt="github")
    return markdown_tb

def format_as_small_rows():
    headers = ["Model","Task", "Results"]
    rows = []
    for data in results_data():
        model_name = data["config_general"]["model_name"]
        for key, value in data["results"].items():
            formatted_metrics = "||".join([f"{key}:{value:.4f}" for key, value in value.items()])

            rows.append([model_name, key, formatted_metrics])
    markdown_tb = tabulate(rows, headers=headers, tablefmt="github")
    return markdown_tb

markdown_tb = format_as_small_rows()
with open("results.md", "w") as f:
    f.write(markdown_tb)

