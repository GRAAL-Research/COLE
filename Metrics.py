import abc
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef
from scipy.stats import pearsonr, spearmanr


class Metrics(abc.ABC):
    def __int__(self, matric: str):
        self.matric = matric

    @abc.abstractmethod
    def compute(self, golds, preds):
        pass


class Accuracy(Metrics):
    def __int__(self):
        super().__init__('accuracy')

    def compute(self, golds, preds):
        return accuracy_score(golds, preds)


class F1(Metrics):
    def __int__(self, average: str = 'micro'):
        name = f'f1_{average}'
        super().__init__(name)
        self.average = average

    def compute(self, golds, preds):
        return f1_score(golds, preds)


class MatthewsCC(Metrics):
    def __init__(self):
        super().__init__('matthews_cc')

    def compute(self, golds, preds):
        return matthews_corrcoef(golds, preds)


class Pearson(Metrics):
    def __int__(self):
        super().__init__('pearson_r')

    def compute(self, golds, preds):
        return pearsonr(golds, preds)[0]


class SpearmanR(Metrics):
    def __int__(self):
        super().__init__('spearman_r')

    def compute(self, golds, preds):
        return spearmanr(golds, preds)[0]


class MetricCollection:

    def __init__(self, metrics):
        self.metrics = metrics

    def compute_all(self, golds, preds):
        results = {}
        for metric in self.metrics:
            results[metric.name] = metric.compute(golds, preds)
        return results
