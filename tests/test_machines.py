import pytest
from turinglab import SingleTapeTM

def run_machine(yaml_path, input_str):
    tm = SingleTapeTM.from_yaml(yaml_path)
    return tm.run(input_str)

# TM-1: Unary to Binary
def test_unary_to_binary():
    path = "machines/unary_to_binary.yaml"
    test_cases = [
        ("111", True, "11"),      # 3
        ("1111", True, "100"),    # 4
        ("1", True, "1"),         # 1
        ("11", True, "10"),       # 2
        ("", True, "0"),          # 0 (Edge case)
    ]
    for inp, expected_acc, expected_tape in test_cases:
        result = run_machine(path, inp)
        assert result.accepted == expected_acc
        assert result.final_tape.strip("B") == expected_tape

# TM-2: Binary Compare
def test_binary_compare():
    path = "machines/binary_compare.yaml"
    test_cases = [
        ("11#10", True),     # 3 > 2 (Accept)
        ("10#11", False),    # 2 > 3 (Reject)
        ("111#11", True),    # Longer N1 (Accept)
        ("1#111", False),    # Longer N2 (Reject)
        ("101#101", False),  # Equal (Reject)
    ]
    for inp, expected_acc in test_cases:
        result = run_machine(path, inp)
        assert result.accepted == expected_acc

# TM-3: String Copy
def test_string_copy():
    path = "machines/string_copy.yaml"
    test_cases = [
        ("abba", True, "abba#abba"),
        ("a", True, "a#a"),
        ("ab", True, "ab#ab"),
        ("", True, "#"),
        ("bbb", True, "bbb#bbb"),
    ]
    for inp, expected_acc, expected_tape in test_cases:
        result = run_machine(path, inp)
        assert result.accepted == expected_acc
        assert result.final_tape.strip("B") == expected_tape

# TM-4: Parenthesis Checker
def test_student_choice():
    path = "machines/student_choice.yaml"
    test_cases = [
        ("(()())", True),
        ("((()))", True),
        ("(()", False),
        ("())", False),
        ("", True),
    ]
    for inp, expected_acc in test_cases:
        result = run_machine(path, inp)
        assert result.accepted == expected_acc
