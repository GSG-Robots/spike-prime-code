"""Types to enable easier overview"""

from typing import Iterator


class Condition(Iterator[tuple[int]]): ...


class Corrector(Iterator[tuple[int, int]]): ...


# Condition = Iterator[tuple[int, int]]
# """Condition type definition
# """
