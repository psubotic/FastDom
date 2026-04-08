"""
cfg.py - Control Flow Graph representation and utilities.
"""
from collections import defaultdict
from typing import Dict, Set, List, Optional


class CFG:
    """A reducible Single-Entry Single-Exit (SESE) Control Flow Graph."""

    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, List[str]] = defaultdict(list)   # node -> successors
        self.pred:  Dict[str, List[str]] = defaultdict(list)   # node -> predecessors
        self.entry: Optional[str] = None
        self.exit:  Optional[str] = None

    def add_edge(self, src: str, dst: str) -> None:
        if src not in self.edges or dst not in self.edges[src]:
            self.edges[src].append(dst)
            self.pred[dst].append(src)
        self.nodes.add(src)
        self.nodes.add(dst)

    def set_entry(self, node: str) -> None:
        self.entry = node
        self.nodes.add(node)

    def set_exit(self, node: str) -> None:
        self.exit = node
        self.nodes.add(node)

    # ------------------------------------------------------------------
    # Reverse post-order (RPO) — Cooper et al. require this ordering
    # ------------------------------------------------------------------
    def reverse_postorder(self) -> List[str]:
        visited: Set[str] = set()
        postorder: List[str] = []

        def dfs(n: str) -> None:
            visited.add(n)
            for s in self.edges.get(n, []):
                if s not in visited:
                    dfs(s)
            postorder.append(n)

        dfs(self.entry)
        return list(reversed(postorder))

    def __repr__(self) -> str:
        lines = [f"CFG(entry={self.entry}, exit={self.exit})"]
        for n in sorted(self.nodes):
            succs = self.edges.get(n, [])
            lines.append(f"  {n} -> {succs}")
        return "\n".join(lines)
