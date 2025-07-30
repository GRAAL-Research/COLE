
export const normalizeBenchmarkName = (name) => {
  const parts = name.toLowerCase().split("|");
  if (parts.length >= 2) return parts[1].replace(/-/g, "_");
  return name.toLowerCase();
};

export const computeAverageScore = (entry) => {
  const allowedMetrics = [
    "acc",
    "accuracy",
    "f1",
    "exact_match",
    "fquad",
    "pearson",
    "pearsonr",
    "spearman",
  ];

  const perTaskAverages = [];

  Object.values(entry.results || {}).forEach((taskData) => {
    if (taskData && typeof taskData === "object") {
      Object.values(taskData).forEach((metricGroup) => {
        if (metricGroup && typeof metricGroup === "object") {
          const taskMetrics = Object.entries(metricGroup)
            .filter(([metric]) => allowedMetrics.includes(metric.toLowerCase()))
            .map(([, value]) =>
              typeof value === "number" ? value : null
            )
            .filter((v) => v !== null);

          if (taskMetrics.length > 0) {
            const normalized = taskMetrics.map((v) => v > 1 ? v / 100 : v);
            const taskAvg = normalized.reduce((a, b) => a + b, 0) / normalized.length;
            perTaskAverages.push(taskAvg);
          }
        }
      });
    }
  });

  if (perTaskAverages.length === 0) return null;

  return perTaskAverages.reduce((a, b) => a + b, 0) / perTaskAverages.length;
};

