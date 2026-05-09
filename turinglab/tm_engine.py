import yaml
import sys
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class Configuration:
    state: str
    tape: str
    head_position: int

@dataclass
class RunResult:
    accepted: bool
    final_tape: str
    steps: int
    history: List[Configuration]
    reason: str

class SingleTapeTM:
    def __init__(self, config_dict: Dict[str, Any]):
        self.config = config_dict
        self.name = config_dict.get('name', 'Turing Machine')
        self.states = config_dict['states']
        self.start_state = config_dict.get('start_state') or config_dict.get('initial_state')
        self.accept_states = config_dict['accept_states']
        self.reject_states = config_dict.get('reject_states', [])
        self.blank = config_dict.get('blank', 'B')
        
        # Standardize transitions: list of dicts -> dict of dicts
        self.transitions = {}
        raw_transitions = config_dict['transitions']
        
        if isinstance(raw_transitions, list):
            for t in raw_transitions:
                state = t['state']
                read_char = t['read']
                if state not in self.transitions:
                    self.transitions[state] = {}
                self.transitions[state][read_char] = (t['next'], t['write'], t['move'])
        else:
            # Fallback for nested dict format if needed, but the spec says list
            self.transitions = raw_transitions

    @classmethod
    def from_yaml(cls, path: str):
        """Loads a Turing Machine from a YAML file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load YAML: {e}")

        required_fields = ['states', 'accept_states', 'transitions']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        if 'start_state' not in config and 'initial_state' not in config:
            raise ValueError("Missing required field: start_state")

        return cls(config)

    def run(self, input_string: str = "", max_steps: int = 1000, verbose: bool = False) -> RunResult:
        """Executes the Turing Machine on the given input string."""
        tape: Dict[int, str] = {i: char for i, char in enumerate(input_string)}
        head_position = 0
        current_state = self.start_state
        steps = 0
        history = []
        reason = ""
        accepted = False

        def get_tape_str(current_tape, head_pos):
            min_idx = min(current_tape.keys()) if current_tape else 0
            max_idx = max(current_tape.keys()) if current_tape else 0
            start = min(min_idx, head_pos)
            end = max(max_idx, head_pos)
            res = ""
            for i in range(start, end + 1):
                res += current_tape.get(i, self.blank)
            return res

        def get_verbose_tape(current_tape, head_pos):
            min_idx = min(current_tape.keys()) if current_tape else 0
            max_idx = max(current_tape.keys()) if current_tape else 0
            start = min(min_idx, head_pos)
            end = max(max_idx, head_pos)
            res = ""
            for i in range(start, end + 1):
                char = current_tape.get(i, self.blank)
                if i == head_pos:
                    res += f"[{char}]"
                else:
                    res += char
            return res

        while steps <= max_steps:
            # Record history BEFORE the step
            tape_str = get_tape_str(tape, head_position)
            history.append(Configuration(state=current_state, tape=tape_str, head_position=head_position))

            # Check if in accept/reject state
            if current_state in self.accept_states:
                accepted = True
                reason = "accept"
                break
            if current_state in self.reject_states:
                accepted = False
                reason = "reject"
                break
            
            # Check timeout (steps is current count, so if we are at max_steps and not halted, it's a timeout)
            if steps == max_steps:
                accepted = False
                reason = "timeout"
                break

            # Find transition
            current_char = tape.get(head_position, self.blank)
            state_trans = self.transitions.get(current_state, {})
            if current_char not in state_trans:
                accepted = False
                reason = "no_transition"
                break

            next_state, write_char, move = state_trans[current_char]
            
            if verbose:
                v_tape = get_verbose_tape(tape, head_position)
                print(f"Adım {steps} | Durum: {current_state} | Şerit: {v_tape} | Hareket: {move}")

            # Apply transition
            tape[head_position] = write_char
            if move == 'R':
                head_position += 1
            elif move == 'L':
                head_position -= 1
            
            current_state = next_state
            steps += 1

        final_tape_str = get_tape_str(tape, head_position)
        return RunResult(
            accepted=accepted,
            final_tape=final_tape_str,
            steps=steps,
            history=history,
            reason=reason
        )

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m turinglab.tm_engine <config_yaml> <input_string>")
    else:
        tm = SingleTapeTM.from_yaml(sys.argv[1])
        result = tm.run(sys.argv[2], verbose=True)
        print(f"\nResult: {'ACCEPTED' if result.accepted else 'REJECTED'} ({result.reason})")
        print(f"Final Tape: {result.final_tape}")
        print(f"Steps: {result.steps}")
