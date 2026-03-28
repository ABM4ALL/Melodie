from typing import Literal, Optional, Sequence


def resolve_parallel_mode(
    parallel_mode: Optional[Literal["process", "thread"]],
    version_info: Optional[Sequence[int]] = None,
) -> Literal["process", "thread"]:
    if parallel_mode in {"process", "thread"}:
        return parallel_mode
    if parallel_mode is not None:
        raise ValueError(f"Unknown parallel_mode: {parallel_mode}")

    if version_info is None:
        import sys

        version_info = sys.version_info

    major, minor = version_info[0], version_info[1]
    return "thread" if (major, minor) >= (3, 13) else "process"
