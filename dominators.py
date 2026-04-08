"""
dominators.py - Cooper et al. (2001) dominator algorithm.

Reference:
  Keith D. Cooper, Timothy J. Harvey, Ken Kennedy.
  "A Simple, Fast Dominance Algorithm."
  Software Practice & Experience, 2001.

Complexity: O(n * d) where d = loop nesting depth (near-linear for reducible CFGs).
"""
from typing import Dict, List, Optional
from cfg import CFG


def _intersect(b1: str, b2: str, rpo_number: Dict[str, int],
               idom: Dict[str, str]) -> str:
    """Walk up the dominator tree from b1 and b2 until they meet."""
    finger1, finger2 = b1, b2
    while finger1 != finger2:
        while rpo_number[finger1] > rpo_number[finger2]:
            finger1 = idom[finger1]
        while rpo_number[finger2] > rpo_number[finger1]:
            finger2 = idom[finger2]
    return finger1


def compute_idoms(cfg: CFG) -> Dict[str, str]:
    """
    Compute the immediate dominator (idom) for every node using
    the Cooper et al. iterative algorithm.

    Returns a dict mapping node -> immediate dominator.
    The entry node maps to itself.
    """
    rpo: List[str] = cfg.reverse_postorder()
    rpo_number: Dict[str, int] = {n: i for i, n in enumerate(rpo)}

    # Initialise: only the entry node has a known idom
    idom: Dict[str, Optional[str]] = {n: None for n in cfg.nodes}
    idom[cfg.entry] = cfg.entry

    changed = True
    while changed:
        changed = False
        for b in rpo:
            if b == cfg.entry:
                continue

            # Processed predecessors (those with idom already set)
            processed_preds = [p for p in cfg.pred.get(b, [])
                               if idom[p] is not None]
            if not processed_preds:
                continue

            # Pick the first processed predecessor as the initial idom
            new_idom = processed_preds[0]

            # Intersect with all other processed predecessors
            for p in processed_preds[1:]:
                new_idom = _intersect(p, new_idom, rpo_number, idom)

            if idom[b] != new_idom:
                idom[b] = new_idom
                changed = True

    return idom  # type: ignore[return-value]


def dominators_of(node: str, idom: Dict[str, str]) -> List[str]:
    """
    Return the full dominator set of *node* (including node itself),
    ordered from the entry (root) down to *node*.
    """
    doms: List[str] = []
    cur = node
    while True:
        doms.append(cur)
        parent = idom[cur]
        if parent == cur:   # entry node is its own idom
            break
        cur = parent
    return list(reversed(doms))


def dominator_tree(idom: Dict[str, str]) -> Dict[str, List[str]]:
    """Return the dominator tree as a dict: parent -> list of children."""
    tree: Dict[str, List[str]] = {n: [] for n in idom}
    for node, parent in idom.items():
        if parent != node:
            tree[parent].append(node)
    return tree
