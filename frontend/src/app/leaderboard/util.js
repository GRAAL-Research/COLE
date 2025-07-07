
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
    "pearson",
    "pearsonr",
    "spearman",
  ];

  const rawValues = [];
  Object.values(entry.results || {}).forEach((taskData) => {
    if (taskData && typeof taskData === "object") {
      Object.values(taskData).forEach((metricGroup) => {
        if (metricGroup && typeof metricGroup === "object") {
          Object.entries(metricGroup)
            .filter(([metric]) =>
              allowedMetrics.includes(metric.toLowerCase())
            )
            .forEach(([, value]) => {
              if (typeof value === "number") {
                rawValues.push(value);
              }
            });
        }
      });
    }
  });

  if (rawValues.length === 0) return null;


  const normalized = rawValues.map((v) =>
    v > 1 ? v / 100 : v
  );
  const sum = normalized.reduce((a, b) => a + b, 0);
  return sum / normalized.length;
};
