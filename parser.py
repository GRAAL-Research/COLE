import  re


def parse_binary_answer(answer:str)->int:
    match = re.search(r'\b[01]\b', answer)
    if match:
        return int(match.group())
    raise ValueError(f"Could not extract '0' or '1' from the answer: {answer!r}")
def parse_ternary_answer(answer:str)->int:
    match = re.search(r'\b[0-2]\b', answer)
    if match:
        return int(match.group())
    raise ValueError(f"Could not extract '0' or '1' or '2' from the answer: {answer!r}")
def parse_float_answer(answer:str)->float:
    match = re.search(r"-?\d+(?:\.\d+)?", answer)
    if match:
        return float(match.group())
    raise ValueError(f"Could not extract a float from the answer: {answer!r}")
def parse_int_range_answer(answer: str, max_val: int) -> int:
    choices = "|".join(str(i) for i in range(max_val + 1))
    pattern = rf"\b(?:{choices})\b"
    match = re.search(pattern, answer)
    if match:
        return int(match.group())
    raise ValueError(f"Could not extract an integer between 0 and {max_val} from the answer: {answer!r}")

