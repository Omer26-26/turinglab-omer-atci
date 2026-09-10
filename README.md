# TuringLab

A Turing machine simulator developed for a Computation Theory course.

**Selcuk University - Computer Engineering**

## Features

- Single-tape deterministic Turing machine with YAML-based configuration, verbose mode, and execution history
- Multi-tape Turing machine with support for multiple tapes and parallel head movement
- Nondeterministic Turing machine with BFS-based computation tree exploration
- Comparative analysis for DTM, multi-tape TM, and NTM performance
- Visualizer that generates step-by-step PNG frames and animated GIF outputs

## Project Structure

```text
turinglab/
├── __init__.py              # Public API
├── tm_engine.py             # Single-tape TM engine
├── multi_tape.py            # Multi-tape TM implementation
├── ntm.py                   # Nondeterministic TM implementation
└── visualizer.py            # Step-by-step visualizer

machines/
├── sample_incrementer.yaml      # Example: binary increment
├── unary_to_binary.yaml         # TM-1: unary to binary converter
├── binary_compare.yaml          # TM-2: binary comparator
├── string_copy.yaml             # TM-3: string copier
├── student_choice.yaml          # TM-4: balanced parentheses checker
├── binary_addition_3tape.yaml   # Multi-tape binary addition
├── contains_01_ntm.yaml         # NTM: checks whether "01" exists
├── contains_01_single.yaml      # DTM: checks whether "01" exists
└── contains_01_multi.yaml       # Multi-tape TM: checks whether "01" exists

tests/
├── test_tm_engine.py        # Engine unit tests
├── test_machines.py         # Integration tests for the four machines
├── test_multi_tape.py       # Multi-tape TM tests
└── test_ntm.py              # NTM tests

docs/
├── design_notes.md          # Design notes
├── comparison_analysis.py   # Comparative analysis script
├── comparison.png           # Performance comparison chart
└── images/                  # Visualizer outputs
```

## Installation

```bash
# Python 3.10+ is required
pip install -r requirements.txt

# Optional visualizer and comparative-analysis dependencies
pip install -r requirements-visualization.txt
```

The core simulators can be imported without the visualization dependencies. `TuringVisualizer` is loaded lazily when requested.

## Usage

### Run a Single-Tape TM

```bash
python -m turinglab.tm_engine machines/sample_incrementer.yaml 1011
```

```python
from turinglab import SingleTapeTM

tm = SingleTapeTM.from_yaml("machines/unary_to_binary.yaml")
result = tm.run("11111", verbose=True)
print(f"Result: {'ACCEPT' if result.accepted else 'REJECT'}")
print(f"Tape: {result.final_tape}")
print(f"Steps: {result.steps}")
```

### Multi-Tape TM

```python
from turinglab.multi_tape import MultiTapeTM

tm = MultiTapeTM.from_yaml("machines/binary_addition_3tape.yaml")
result = tm.run("11#01")  # 3 + 1 = 4
```

### Nondeterministic TM

```python
from turinglab.ntm import NondeterministicTM

ntm = NondeterministicTM.from_yaml("machines/contains_01_ntm.yaml")
result = ntm.run("1101", max_depth=50, max_branches=1000)
print(f"Accepting paths: {len(result.accepting_paths)}")
```

### Visualizer

```python
from turinglab import SingleTapeTM
from turinglab.visualizer import TuringVisualizer

tm = SingleTapeTM.from_yaml("machines/sample_incrementer.yaml")
result = tm.run("1011")

vis = TuringVisualizer(result.history, machine_name="Binary Increment", accepted=result.accepted)
vis.generate_frames("docs/images/")
vis.generate_gif("docs/images/animation.gif")
```

## Tests

```bash
python -m pytest tests/ -v

python -m pytest tests/test_tm_engine.py -v
python -m pytest tests/test_machines.py -v
python -m pytest tests/test_multi_tape.py -v
python -m pytest tests/test_ntm.py -v
```

## Comparative Analysis

The same language, `L = {w | w contains "01"}`, is solved with three Turing machine variants and compared by step count.

```bash
python docs/comparison_analysis.py
# Output: docs/comparison.png
```

See [REPORT.md](REPORT.md) for details.

## Design Notes

The tape is represented with `Dict[int, str]`, which provides negative index support and models an infinite tape.

More details: [docs/design_notes.md](docs/design_notes.md) and [REPORT.md](REPORT.md).

## License

This project is licensed under the [MIT License](LICENSE).

