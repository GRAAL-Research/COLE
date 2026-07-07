from collections import Counter
from typing import Any, List
import sympy as sp


def clean_parentheses(text: str) -> str:
    """Removes outer parentheses/brackets only if they enclose the entire expression."""
    text = text.strip()
    if not text:
        return text

    # Check for matching parentheses ()
    if text.startswith("(") and text.endswith(")"):
        balance = 0
        encloses_all = True
        for i, char in enumerate(text):
            if char == "(":
                balance += 1
            elif char == ")":
                balance -= 1
                if balance == 0 and i < len(text) - 1:
                    encloses_all = False
                    break
        if encloses_all:
            return text[1:-1].strip()

    # Check for matching brackets []
    if text.startswith("[") and text.endswith("]"):
        balance = 0
        encloses_all = True
        for i, char in enumerate(text):
            if char == "[":
                balance += 1
            elif char == "]":
                balance -= 1
                if balance == 0 and i < len(text) - 1:
                    encloses_all = False
                    break
        if encloses_all:
            return text[1:-1].strip()

    return text


def parse_single_math_token(token: str) -> Any:
    """Parses a single mathematical token to a float, SymPy expression, or string fallback."""
    token = token.strip().lower()
    if not token:
        return None

    # Try parsing as float (handles standard numbers, e.g. 5, 24.14)
    try:
        return float(token)
    except ValueError:
        pass

    # Try parsing as SymPy expression (handles algebra like x+y, fractions like 1/2)
    try:
        # Standardize exponentiation syntax for SymPy
        cleaned = token.replace("^", "**")
        expr = sp.sympify(cleaned)
        if expr is not None:
            return expr
    except Exception:
        pass

    # Fallback to normalized lowercase string
    return token.lower()


def parse_math_expression(text: str) -> Any:
    """Parses a mathematical expression, list, coordinate, or fallback text.

    Handles:
    - Lists/coords like (24, 14) -> (24.0, 14.0)
    - Fractions like 1/2 -> 0.5 (or sympy Rational)
    - Algebraic expressions like x + y -> Symbol('x') + Symbol('y')
    - Fallback text like 'Section A' -> 'section a'
    """
    text = text.strip()
    if not text:
        return ""

    cleaned_text = clean_parentheses(text)

    # Check if it's a comma-separated or space-separated list of numbers/expressions
    if "," in cleaned_text:
        parts = cleaned_text.split(",")
        parsed_parts = [parse_single_math_token(p) for p in parts if p.strip()]
        if parsed_parts:
            return tuple(parsed_parts)

    # Try parsing the whole expression (after cleaning outer parentheses)
    return parse_single_math_token(cleaned_text)


def check_mathematical_equivalence(val1: Any, val2: Any) -> bool:
    # pylint: disable=too-many-return-statements
    """Determines if two parsed math values are equivalent."""
    if isinstance(val1, sp.Basic) and isinstance(val2, sp.Basic):
        try:
            return sp.simplify(val1 - val2) == 0
        except Exception:
            return False

    if type(val1) != type(val2):
        # Allow comparing float with SymPy number
        if isinstance(val1, (float, int)) and isinstance(val2, sp.Basic):
            try:
                return sp.simplify(val1 - val2) == 0
            except Exception:
                return False
        if isinstance(val2, (float, int)) and isinstance(val1, sp.Basic):
            try:
                return sp.simplify(val2 - val1) == 0
            except Exception:
                return False
        return False

    if isinstance(val1, tuple):
        if len(val1) != len(val2):
            return False
        return all(check_mathematical_equivalence(x, y) for x, y in zip(val1, val2))

    return val1 == val2


def math_exact_match_score(prediction: str, ground_truth: str) -> bool:
    """Returns True if prediction is mathematically equivalent to the ground truth."""
    pred_parsed = parse_math_expression(prediction)
    gt_parsed = parse_math_expression(ground_truth)
    return check_mathematical_equivalence(pred_parsed, gt_parsed)


def math_f1_score(prediction: str, ground_truth: str) -> float:
    """Returns 1.0 if mathematically equivalent, otherwise computes token-level F1
    using basic math tokenization (preserving numbers and symbols).
    """
    if math_exact_match_score(prediction, ground_truth):
        return 1.0

    # Basic tokenization fallback that keeps math symbols and numbers together
    def tokenize(text: str) -> List[str]:
        # Replace operators and punctuation with space-padded versions to ensure uniform tokenization
        cleaned = []
        for c in text.lower():
            if c.isalnum() or c == ".":
                cleaned.append(c)
            elif c in "+-*/^(),":
                cleaned.append(f" {c} ")
            else:
                cleaned.append(" ")
        return [t for t in "".join(cleaned).split() if t]

    pred_tokens = tokenize(prediction)
    gt_tokens = tokenize(ground_truth)

    if not pred_tokens or not gt_tokens:
        return 0.0

    common = Counter(pred_tokens) & Counter(gt_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = 1.0 * num_same / len(pred_tokens)
    recall = 1.0 * num_same / len(gt_tokens)
    return (2 * precision * recall) / (precision + recall)
