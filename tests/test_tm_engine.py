import pytest
import yaml
import io
from contextlib import redirect_stdout
from turinglab import SingleTapeTM, RunResult

# Helper to create a temporary YAML config
def create_temp_config(tmp_path, config, filename="test_config.yaml"):
    config_file = tmp_path / filename
    with open(config_file, "w") as f:
        yaml.dump(config, f)
    return str(config_file)

@pytest.fixture
def binary_increment_config():
    return {
        "name": "binary_increment",
        "states": ["q0", "q_back", "q_carry", "q_done", "q_accept"],
        "start_state": "q0",
        "accept_states": ["q_accept"],
        "transitions": [
            {"state": "q0", "read": "0", "next": "q0", "write": "0", "move": "R"},
            {"state": "q0", "read": "1", "next": "q0", "write": "1", "move": "R"},
            {"state": "q0", "read": "B", "next": "q_back", "write": "B", "move": "L"},
            {"state": "q_back", "read": "0", "next": "q_done", "write": "1", "move": "L"},
            {"state": "q_back", "read": "1", "next": "q_back", "write": "0", "move": "L"},
            {"state": "q_back", "read": "B", "next": "q_done", "write": "1", "move": "L"},
            {"state": "q_done", "read": "0", "next": "q_done", "write": "0", "move": "L"},
            {"state": "q_done", "read": "1", "next": "q_done", "write": "1", "move": "L"},
            {"state": "q_done", "read": "B", "next": "q_accept", "write": "B", "move": "R"}
        ]
    }

def test_handbook_example_binary_increment(tmp_path, binary_increment_config):
    config_path = create_temp_config(tmp_path, binary_increment_config)
    tm = SingleTapeTM.from_yaml(config_path)
    
    inputs = {
        "1011": "1100",
        "111": "1000",
        "0": "1",
        "10": "11",
        "": "1"
    }
    
    for inp, expected in inputs.items():
        result = tm.run(inp)
        assert result.accepted is True
        assert result.final_tape.strip("B") == expected

def test_timeout(tmp_path):
    config = {
        "states": ["q0"],
        "start_state": "q0",
        "accept_states": ["q_acc"],
        "transitions": [
            {"state": "q0", "read": "B", "next": "q0", "write": "B", "move": "R"}
        ]
    }
    config_path = create_temp_config(tmp_path, config)
    tm = SingleTapeTM.from_yaml(config_path)
    result = tm.run("", max_steps=10)
    assert result.accepted is False
    assert result.reason == "timeout"
    assert result.steps == 10

def test_no_transition(tmp_path):
    config = {
        "states": ["q0"],
        "start_state": "q0",
        "accept_states": ["q_acc"],
        "transitions": []
    }
    config_path = create_temp_config(tmp_path, config)
    tm = SingleTapeTM.from_yaml(config_path)
    result = tm.run("1")
    assert result.accepted is False
    assert result.reason == "no_transition"

def test_invalid_yaml(tmp_path):
    config_path = tmp_path / "invalid.yaml"
    with open(config_path, "w") as f:
        f.write("invalid: yaml: :")
    with pytest.raises(ValueError):
        SingleTapeTM.from_yaml(str(config_path))

def test_missing_fields(tmp_path):
    config = {"states": ["q0"]}
    config_path = create_temp_config(tmp_path, config)
    with pytest.raises(ValueError):
        SingleTapeTM.from_yaml(config_path)

def test_verbose_output(tmp_path):
    config = {
        "states": ["q0", "q_acc"],
        "start_state": "q0",
        "accept_states": ["q_acc"],
        "transitions": [
            {"state": "q0", "read": "1", "next": "q_acc", "write": "0", "move": "R"}
        ]
    }
    config_path = create_temp_config(tmp_path, config)
    tm = SingleTapeTM.from_yaml(config_path)
    
    f = io.StringIO()
    with redirect_stdout(f):
        tm.run("1", verbose=True)
    output = f.getvalue()
    
    assert "Adım 0 | Durum: q0 | Şerit: [1] | Hareket: R" in output

def test_history_tracking(tmp_path):
    config = {
        "states": ["q0", "q1", "q_acc"],
        "start_state": "q0",
        "accept_states": ["q_acc"],
        "transitions": [
            {"state": "q0", "read": "1", "next": "q1", "write": "X", "move": "R"},
            {"state": "q1", "read": "B", "next": "q_acc", "write": "B", "move": "S"}
        ]
    }
    config_path = create_temp_config(tmp_path, config)
    tm = SingleTapeTM.from_yaml(config_path)
    result = tm.run("1")
    
    assert len(result.history) >= 2
    assert result.history[0].state == "q0"
    assert result.history[0].tape == "1"
    assert result.history[1].state == "q1"
    # After first step, tape at index 0 is X, head at pos 1 is B
    assert result.history[1].tape == "XB" 

def test_reject_reason(tmp_path):
    config = {
        "states": ["q0", "q_rej"],
        "start_state": "q0",
        "accept_states": ["q_acc"],
        "reject_states": ["q_rej"],
        "transitions": [
            {"state": "q0", "read": "0", "next": "q_rej", "write": "0", "move": "S"}
        ]
    }
    config_path = create_temp_config(tmp_path, config)
    tm = SingleTapeTM.from_yaml(config_path)
    result = tm.run("0")
    assert result.accepted is False
    assert result.reason == "reject"

def test_left_overflow(tmp_path):
    # Requirement says "Karar size ait — README'de belirtin"
    # My implementation allows negative indices.
    config = {
        "states": ["q0", "q_acc"],
        "start_state": "q0",
        "accept_states": ["q_acc"],
        "transitions": [
            {"state": "q0", "read": "1", "next": "q_acc", "write": "1", "move": "L"}
        ]
    }
    config_path = create_temp_config(tmp_path, config)
    tm = SingleTapeTM.from_yaml(config_path)
    result = tm.run("1")
    assert result.accepted is True
    assert result.history[-1].head_position == -1
    assert result.final_tape == "B1" # B at -1, 1 at 0
