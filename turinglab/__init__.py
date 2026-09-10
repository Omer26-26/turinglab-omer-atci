from typing import TYPE_CHECKING, Any

from .tm_engine import SingleTapeTM, RunResult, Configuration
from .multi_tape import MultiTapeTM, MultiTapeConfiguration
from .ntm import NondeterministicTM, NTMRunResult

if TYPE_CHECKING:
    from .visualizer import TuringVisualizer

__version__ = "1.0.0"

__all__ = [
    "Configuration",
    "MultiTapeConfiguration",
    "MultiTapeTM",
    "NTMRunResult",
    "NondeterministicTM",
    "RunResult",
    "SingleTapeTM",
    "TuringVisualizer",
]


def __getattr__(name: str) -> Any:
    """Load visualization support only when it is requested."""
    if name != "TuringVisualizer":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    try:
        from .visualizer import TuringVisualizer
    except ModuleNotFoundError as exc:
        if exc.name == "PIL":
            raise ModuleNotFoundError(
                "TuringVisualizer requires the visualization dependencies. "
                "Install them with 'pip install -r requirements-visualization.txt'."
            ) from exc
        raise

    return TuringVisualizer
