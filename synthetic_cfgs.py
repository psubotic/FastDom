"""
synthetic_cfgs.py - Generators for synthetic reducible SESE CFGs.

All graphs are reducible (no irreducible loops) and have a single
entry and single exit node.

Available graphs
----------------
linear          : straight-line sequence  entry -> n1 -> n2 -> ... -> exit
diamond         : if/else diamond
nested_if       : nested if-else
single_loop     : simple while loop
nested_loops    : doubly nested while loops
loop_with_break : loop with a mid-body branch to exit
complex         : combination of loops, conditionals, and merges
"""
from cfg import CFG


def linear(n: int = 5) -> CFG:
    """
    entry -> A -> B -> ... -> exit   (n total interior nodes)
    """
    g = CFG()
    nodes = ["entry"] + [f"n{i}" for i in range(n)] + ["exit"]
    g.set_entry("entry")
    g.set_exit("exit")
    for i in range(len(nodes) - 1):
        g.add_edge(nodes[i], nodes[i + 1])
    return g


def diamond() -> CFG:
    """
    entry
      |
    cond
    /    \\
  then   else
    \\   /
     merge
      |
     exit
    """
    g = CFG()
    g.set_entry("entry")
    g.set_exit("exit")
    for s, d in [("entry", "cond"), ("cond", "then"), ("cond", "else"),
                 ("then", "merge"), ("else", "merge"), ("merge", "exit")]:
        g.add_edge(s, d)
    return g


def nested_if() -> CFG:
    """
    entry -> outer_cond
               /         \\
           inner_cond    else_outer
            /    \\           |
         then   else_inner  |
           \\    /            |
           merge_inner       |
                 \\          /
                  merge_outer
                      |
                     exit
    """
    g = CFG()
    g.set_entry("entry")
    g.set_exit("exit")
    edges = [
        ("entry",       "outer_cond"),
        ("outer_cond",  "inner_cond"),
        ("outer_cond",  "else_outer"),
        ("inner_cond",  "then"),
        ("inner_cond",  "else_inner"),
        ("then",        "merge_inner"),
        ("else_inner",  "merge_inner"),
        ("merge_inner", "merge_outer"),
        ("else_outer",  "merge_outer"),
        ("merge_outer", "exit"),
    ]
    for s, d in edges:
        g.add_edge(s, d)
    return g


def single_loop() -> CFG:
    """
    entry -> pre_loop -> loop_header -> loop_body -> loop_header (back edge)
                                    \\-> post_loop -> exit
    """
    g = CFG()
    g.set_entry("entry")
    g.set_exit("exit")
    edges = [
        ("entry",       "pre_loop"),
        ("pre_loop",    "loop_header"),
        ("loop_header", "loop_body"),
        ("loop_header", "post_loop"),
        ("loop_body",   "loop_header"),   # back edge (reducible)
        ("post_loop",   "exit"),
    ]
    for s, d in edges:
        g.add_edge(s, d)
    return g


def nested_loops() -> CFG:
    """
    entry -> outer_header -> inner_header -> inner_body -> inner_header (back)
                          \\-> inner_exit -> outer_body -> outer_header (back)
                          \\-> outer_exit -> exit
    """
    g = CFG()
    g.set_entry("entry")
    g.set_exit("exit")
    edges = [
        ("entry",        "outer_header"),
        ("outer_header", "inner_header"),
        ("outer_header", "outer_exit"),
        ("inner_header", "inner_body"),
        ("inner_header", "inner_exit"),
        ("inner_body",   "inner_header"),  # inner back edge
        ("inner_exit",   "outer_body"),
        ("outer_body",   "outer_header"),  # outer back edge
        ("outer_exit",   "exit"),
    ]
    for s, d in edges:
        g.add_edge(s, d)
    return g


def loop_with_break() -> CFG:
    """
    entry -> loop_header -> body_a -> cond -> body_b -> loop_header (back)
                        \\-> post           \\-> post (break)
                                               |
                                             exit
    """
    g = CFG()
    g.set_entry("entry")
    g.set_exit("exit")
    edges = [
        ("entry",       "loop_header"),
        ("loop_header", "body_a"),
        ("loop_header", "post"),
        ("body_a",      "cond"),
        ("cond",        "body_b"),
        ("cond",        "post"),            # break
        ("body_b",      "loop_header"),     # back edge
        ("post",        "exit"),
    ]
    for s, d in edges:
        g.add_edge(s, d)
    return g


def complex_cfg() -> CFG:
    """
    A richer graph combining loops, nested ifs, and multiple merges.

    entry -> A -> loop1_header -> B -> if_cond -> C -> loop1_header (back)
                               \\-> D             \\-> E -> merge1 -> F -> loop2_header
                                                      D --------^          \\-> G -> loop2_header (back)
                                                                            \\-> exit
    """
    g = CFG()
    g.set_entry("entry")
    g.set_exit("exit")
    edges = [
        ("entry",        "A"),
        ("A",            "loop1_header"),
        ("loop1_header", "B"),
        ("loop1_header", "D"),
        ("B",            "if_cond"),
        ("if_cond",      "C"),
        ("if_cond",      "E"),
        ("C",            "loop1_header"),   # back edge
        ("E",            "merge1"),
        ("D",            "merge1"),
        ("merge1",       "F"),
        ("F",            "loop2_header"),
        ("loop2_header", "G"),
        ("loop2_header", "exit"),
        ("G",            "loop2_header"),   # back edge
    ]
    for s, d in edges:
        g.add_edge(s, d)
    return g


AVAILABLE: dict = {
    "linear":         lambda: linear(5),
    "diamond":        diamond,
    "nested_if":      nested_if,
    "single_loop":    single_loop,
    "nested_loops":   nested_loops,
    "loop_with_break": loop_with_break,
    "complex":        complex_cfg,
}
