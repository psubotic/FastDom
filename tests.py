"""
tests.py - Unit tests for the Cooper et al. dominator algorithm.

Run with:  python tests.py
"""
import unittest
from cfg import CFG
from dominators import compute_idoms, dominators_of, dominator_tree
from synthetic_cfgs import (
    linear, diamond, nested_if, single_loop, nested_loops,
    loop_with_break, complex_cfg,
)


class TestLinear(unittest.TestCase):
    def setUp(self):
        self.cfg = linear(3)
        self.idom = compute_idoms(self.cfg)

    def test_entry_dominates_all(self):
        for n in self.cfg.nodes:
            doms = dominators_of(n, self.idom)
            self.assertIn("entry", doms)

    def test_chain_dominators(self):
        # entry -> n0 -> n1 -> n2 -> exit
        # dominators of n2: entry, n0, n1, n2
        doms = dominators_of("n2", self.idom)
        self.assertEqual(doms, ["entry", "n0", "n1", "n2"])

    def test_idom_chain(self):
        self.assertEqual(self.idom["n1"], "n0")
        self.assertEqual(self.idom["n0"], "entry")


class TestDiamond(unittest.TestCase):
    def setUp(self):
        self.cfg = diamond()
        self.idom = compute_idoms(self.cfg)

    def test_then_dominated_by_cond(self):
        doms = dominators_of("then", self.idom)
        self.assertIn("cond", doms)
        self.assertNotIn("else", doms)

    def test_merge_dominated_by_cond_not_branches(self):
        doms = dominators_of("merge", self.idom)
        self.assertIn("cond", doms)
        self.assertNotIn("then", doms)
        self.assertNotIn("else", doms)

    def test_exit_dominated_by_merge(self):
        doms = dominators_of("exit", self.idom)
        self.assertIn("merge", doms)

    def test_idom_merge_is_cond(self):
        self.assertEqual(self.idom["merge"], "cond")


class TestSingleLoop(unittest.TestCase):
    def setUp(self):
        self.cfg = single_loop()
        self.idom = compute_idoms(self.cfg)

    def test_loop_body_dominated_by_header(self):
        doms = dominators_of("loop_body", self.idom)
        self.assertIn("loop_header", doms)

    def test_loop_header_not_dominated_by_body(self):
        doms = dominators_of("loop_header", self.idom)
        self.assertNotIn("loop_body", doms)

    def test_idom_loop_body_is_header(self):
        self.assertEqual(self.idom["loop_body"], "loop_header")

    def test_idom_post_loop_is_header(self):
        self.assertEqual(self.idom["post_loop"], "loop_header")


class TestNestedLoops(unittest.TestCase):
    def setUp(self):
        self.cfg = nested_loops()
        self.idom = compute_idoms(self.cfg)

    def test_inner_body_dominated_by_inner_header(self):
        doms = dominators_of("inner_body", self.idom)
        self.assertIn("inner_header", doms)
        self.assertIn("outer_header", doms)

    def test_inner_header_idom_is_outer_header(self):
        self.assertEqual(self.idom["inner_header"], "outer_header")

    def test_outer_body_dominated_by_outer_header(self):
        # outer_body is only reachable through inner_exit which is only
        # reachable through inner_header, so inner_header does dominate it.
        # But outer_body should NOT be dominated by inner_body.
        doms = dominators_of("outer_body", self.idom)
        self.assertIn("outer_header", doms)
        self.assertNotIn("inner_body", doms)


class TestNestedIf(unittest.TestCase):
    def setUp(self):
        self.cfg = nested_if()
        self.idom = compute_idoms(self.cfg)

    def test_then_idom_is_inner_cond(self):
        self.assertEqual(self.idom["then"], "inner_cond")

    def test_merge_outer_idom_is_outer_cond(self):
        self.assertEqual(self.idom["merge_outer"], "outer_cond")

    def test_merge_inner_idom_is_inner_cond(self):
        self.assertEqual(self.idom["merge_inner"], "inner_cond")


class TestLoopWithBreak(unittest.TestCase):
    def setUp(self):
        self.cfg = loop_with_break()
        self.idom = compute_idoms(self.cfg)

    def test_post_idom_is_loop_header(self):
        # Both the normal exit and break paths merge at 'post',
        # whose sole dominator above it is loop_header
        self.assertEqual(self.idom["post"], "loop_header")

    def test_cond_dominated_by_body_a(self):
        doms = dominators_of("cond", self.idom)
        self.assertIn("body_a", doms)


class TestDominatorTree(unittest.TestCase):
    def test_tree_root_is_entry(self):
        cfg = diamond()
        idom = compute_idoms(cfg)
        tree = dominator_tree(idom)
        # entry should have children but no parent in tree values except itself
        self.assertIn("entry", tree)

    def test_tree_covers_all_nodes(self):
        for factory in [linear, diamond, nested_if, single_loop,
                        nested_loops, loop_with_break, complex_cfg]:
            cfg = factory()
            idom = compute_idoms(cfg)
            tree = dominator_tree(idom)
            self.assertEqual(set(tree.keys()), cfg.nodes)


class TestEntryNode(unittest.TestCase):
    def test_entry_only_dominated_by_itself(self):
        for factory in [linear, diamond, single_loop, nested_loops]:
            cfg = factory()
            idom = compute_idoms(cfg)
            doms = dominators_of(cfg.entry, idom)
            self.assertEqual(doms, [cfg.entry])


if __name__ == "__main__":
    unittest.main(verbosity=2)
