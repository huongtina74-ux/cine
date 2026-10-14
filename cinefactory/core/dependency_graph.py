from __future__ import annotations

from collections import defaultdict, deque


class DependencyGraph:
    """Tracks production dependencies so upstream changes only invalidate affected descendants."""

    def __init__(self) -> None:
        self._children: dict[str, set[str]] = defaultdict(set)
        self._parents: dict[str, set[str]] = defaultdict(set)

    def add_edge(self, upstream: str, downstream: str) -> None:
        self._children[upstream].add(downstream)
        self._parents[downstream].add(upstream)

    def descendants(self, node: str) -> set[str]:
        result: set[str] = set()
        queue = deque([node])
        while queue:
            current = queue.popleft()
            for child in self._children.get(current, ()):
                if child not in result:
                    result.add(child)
                    queue.append(child)
        return result

    def invalidate_from(self, node: str) -> set[str]:
        return self.descendants(node)
