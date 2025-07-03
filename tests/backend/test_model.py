import pytest
from transformers import PreTrainedTokenizerBase

from src.Backend.model import ZipInferenceModel


class Req:
    def __init__(self, prompt, choices, task_name):
        self.prompt = prompt
        self.choices = choices
        self.task_name = task_name

@pytest.fixture
def simple_tokenizer():
    """Minimal tokenizer stub"""
    class Tok(PreTrainedTokenizerBase):
        def __init__(self):
            self.model_max_length = 128
            super().__init__()
        def add_special_tokens(self, token_dict):
            self.special_tokens = token_dict
    return Tok()


@pytest.mark.parametrize("preds,expected", [
    ({"qfrcola": [0]}, ["0"]),
    ({"qfrcola": [1]}, ["1"]),
])
def test_binary_predictions(preds, expected):
    reqs = [Req("anything", ["0", "1"], "qfrcola")]
    model = ZipInferenceModel(preds, tokenizer=PreTrainedTokenizerBase())
    out = [r.get_result_for_eval() for r in model.infer(reqs)]
    assert out == expected

@pytest.mark.parametrize("zero_preds,one_preds,choices", [
    ({"bar": [0,0,0]}, {"bar": [1,1,1]}, ["A", "B", "C"]),
])
def test_multi_request_parametrized(zero_preds, one_preds, choices):
    reqs = [Req(f"p{i+1}", choices, "bar") for i in range(3)]
    model0 = ZipInferenceModel(zero_preds, tokenizer=PreTrainedTokenizerBase())
    model1 = ZipInferenceModel(one_preds, tokenizer=PreTrainedTokenizerBase())
    out0 = [r.get_result_for_eval() for r in model0.infer(reqs)]
    out1 = [r.get_result_for_eval() for r in model1.infer(reqs)]
    assert out0 == [choices[0]] * 3
    assert out1 == [choices[1]] * 3
    assert out0 != out1

@pytest.mark.parametrize("invalid_pred", [5, -1, "x"])
def test_invalid_index_falls_back_to_first_choice(invalid_pred):
    reqs = [Req("qfrcola", ["X", "Y"], "baz")]
    model = ZipInferenceModel({"baz": [invalid_pred]}, tokenizer=PreTrainedTokenizerBase())
    out = [r.get_result_for_eval() for r in model.infer(reqs)]
    assert out == ["X"]



class Cond:
    def __init__(self, task_name):
        self.task_name = task_name

@pytest.mark.parametrize("preds,choices,expected", [
    ({"qfrcola": [0, 1]}, ["X", "Y"], ["X", "Y"]),
])
def test_infer_with_conditions(preds, choices, expected):
    reqs = [Req(f"p{i}", choices, None) for i in range(len(choices))]
    conds = [Cond("x|qfrcola")]
    model = ZipInferenceModel(preds, tokenizer=PreTrainedTokenizerBase())
    outputs = model.infer(reqs, conditions=conds)
    results = [r.get_result_for_eval() for r in outputs]
    assert results == expected
