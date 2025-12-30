from dataclasses import dataclass


@dataclass
class _State:
    verbose: bool = False


state = _State()
