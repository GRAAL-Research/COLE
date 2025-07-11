import matplotlib.pyplot as plt
import numpy as np
from predictions.convert_results_to_md import results_data
import math


def extract_plot_task_data(all_tasks_data, task):
    task_data = all_tasks_data[task]
    models = []
    task_metrics = {}
    for model, model_metrics in task_data.items():
        models.append(model)
        for metric, results in model_metrics.items():
            if metric in task_metrics.keys():
                task_metrics[metric].append(results)
            else:
                task_metrics[metric] = [results]

    return models, task_metrics

def extract_data_by_tasks():
    labels = []
    all_tasks = {}
    datas = results_data()
    for data in datas:
        model_name = data["model_name"]
        for task in data["tasks"]:
            for task_name, metrics_values in task.items():
                for metric_name, metric_values in metrics_values.items():
                    if task_name not in all_tasks.keys():
                        all_tasks[task_name] = {model_name: {metric_key: metric_value for metric_key,metric_value in metric_values.items() if isinstance(metric_value, (int, float))}}
                    else:
                        all_tasks[task_name][model_name] = {metric_key: metric_value for metric_key,metric_value in metric_values.items() if isinstance(metric_value, (int, float))}

    print(all_tasks)
    return all_tasks

all_tasks = extract_data_by_tasks()

labels, metrics = extract_plot_task_data(all_tasks, "piaf")
print(metrics)

num_plots = len(all_tasks)
cols = 3  # or 2, 4 — adjust as needed
rows = math.ceil(num_plots / cols)

fig, axs = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
axs = axs.flatten()  # flatten to 1D list for easier indexing

for i, dataset_name in enumerate(all_tasks.keys()):
    labels, metrics = extract_plot_task_data(all_tasks, dataset_name)
    x = np.arange(len(labels))
    bar_width = 0.8 / len(metrics)

    ax = axs[i]  # Select the i-th subplot

    for j, (key, values) in enumerate(metrics.items()):
        offset = (j - len(metrics) / 2) * bar_width + bar_width / 2
        ax.bar(x + offset, values, bar_width, label=key)

    labels = [s.split("/")[-1] for s in labels]
    ax.set_ylim(top=1)
    ax.set_xlabel("Models")
    ax.set_ylabel("Score")
    ax.set_title(dataset_name)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=-45)
    ax.legend(fontsize=7)

# Hide unused subplots if any
for j in range(i + 1, len(axs)):
    fig.delaxes(axs[j])

plt.tight_layout()
plt.show()
