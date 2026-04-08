#!/usr/bin/env python3
"""
main.py - Interactive CLI for computing dominators on synthetic reducible
          SESE CFGs using the Cooper et al. (2001) algorithm.

Usage
-----
  python main.py                          # interactive prompt
  python main.py --cfg diamond --node merge
  python main.py --cfg single_loop --node loop_body --show-tree
  python main.py --list                   # list available CFGs and their nodes
"""
import argparse
import sys
from synthetic_cfgs import AVAILABLE
from dominators import compute_idoms, dominators_of, dominator_tree


# ── pretty-printing helpers ────────────────────────────────────────────────────

def _print_cfg(cfg) -> None:
    rpo = cfg.reverse_postorder()
    print(f"\n  Entry : {cfg.entry}")
    print(f"  Exit  : {cfg.exit}")
    print(f"  Nodes ({len(cfg.nodes)}): {', '.join(rpo)}")
    print("  Edges:")
    for n in rpo:
        succs = cfg.edges.get(n, [])
        if succs:
            for s in succs:
                back = " ← back edge" if cfg.reverse_postorder().index(s) < cfg.reverse_postorder().index(n) else ""
                print(f"    {n:20s} → {s}{back}")


def _print_tree(tree: dict, root: str, prefix: str = "", last: bool = True) -> None:
    connector = "└── " if last else "├── "
    print(prefix + connector + root)
    children = sorted(tree.get(root, []))
    for i, child in enumerate(children):
        extension = "    " if last else "│   "
        _print_tree(tree, child, prefix + extension, i == len(children) - 1)


# ── core logic ─────────────────────────────────────────────────────────────────

def run(cfg_name: str, node: str, show_tree: bool = False) -> None:
    if cfg_name not in AVAILABLE:
        print(f"[ERROR] Unknown CFG '{cfg_name}'. "
              f"Available: {', '.join(sorted(AVAILABLE))}")
        sys.exit(1)

    cfg = AVAILABLE[cfg_name]()

    if node not in cfg.nodes:
        print(f"[ERROR] Node '{node}' not found in CFG '{cfg_name}'.")
        print(f"        Available nodes: {', '.join(sorted(cfg.nodes))}")
        sys.exit(1)

    print(f"\n{'═'*60}")
    print(f"  CFG  : {cfg_name}")
    _print_cfg(cfg)

    idom = compute_idoms(cfg)
    doms = dominators_of(node, idom)

    print(f"\n{'─'*60}")
    print(f"  Query node : {node}")
    print(f"  Dominators : {' → '.join(doms)}")
    print(f"  (read left-to-right: entry dominates first, then increasingly closer)")

    if node != cfg.entry:
        print(f"  Immediate dominator (idom) : {idom[node]}")

    if show_tree:
        print(f"\n{'─'*60}")
        print("  Dominator Tree:")
        tree = dominator_tree(idom)
        _print_tree(tree, cfg.entry)

    print(f"{'═'*60}\n")


def interactive() -> None:
    print("\n╔══════════════════════════════════════════════════╗")
    print("║  Dominator Finder — Cooper et al. (2001)         ║")
    print("║  Reducible SESE CFGs                             ║")
    print("╚══════════════════════════════════════════════════╝")

    print(f"\nAvailable CFGs: {', '.join(sorted(AVAILABLE))}")
    cfg_name = input("Select CFG: ").strip()
    if cfg_name not in AVAILABLE:
        print(f"Unknown CFG. Choose from: {', '.join(sorted(AVAILABLE))}")
        sys.exit(1)

    cfg = AVAILABLE[cfg_name]()
    rpo = cfg.reverse_postorder()
    print(f"Nodes (RPO): {', '.join(rpo)}")

    node = input("Enter node to query: ").strip()
    show = input("Show full dominator tree? [y/N]: ").strip().lower() == "y"
    run(cfg_name, node, show_tree=show)


def list_cfgs() -> None:
    print("\nAvailable CFGs and their nodes:\n")
    for name in sorted(AVAILABLE):
        cfg = AVAILABLE[name]()
        rpo = cfg.reverse_postorder()
        print(f"  {name}")
        print(f"    nodes : {', '.join(rpo)}")
        print(f"    entry : {cfg.entry}   exit : {cfg.exit}")
        print()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute dominators on reducible SESE CFGs (Cooper et al. 2001)"
    )
    parser.add_argument("--cfg",  help="Name of the synthetic CFG to use")
    parser.add_argument("--node", help="Node to compute dominators for")
    parser.add_argument("--show-tree", action="store_true",
                        help="Print the full dominator tree")
    parser.add_argument("--list", action="store_true",
                        help="List all available CFGs and their nodes")
    args = parser.parse_args()

    if args.list:
        list_cfgs()
    elif args.cfg and args.node:
        run(args.cfg, args.node, show_tree=args.show_tree)
    else:
        interactive()


if __name__ == "__main__":
    main()
