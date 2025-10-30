import os

import pandas as pd

path = os.path.join("llm_details.csv")
export_path = os.path.join("results", "llm_details.tex")
data = pd.read_csv(path, sep="\t")

df_sorted = (
    data.sort_values("model_name", ascending=True)
    .reset_index(drop=True)
)

top_n = int(len(df_sorted) / 2)
left = df_sorted.iloc[:top_n].reset_index(drop=True)
right = df_sorted.iloc[top_n : ].reset_index(drop=True)
right = right.reindex(range(len(left)))
right["model_name"] = right["model_name"].fillna("")

df_2 = pd.DataFrame(
    {
        "model_name": left["model_name"],
        "source": left["source"],
        "size": left["size"],
        "model_name_2": right["model_name"],
        "source_2": right["source"],
        "size_2": right["size"],
    }
)

df_2.to_latex(
    export_path, index=False, float_format="%.2f", escape=False
)