# FastDom
Computes **dominators** for any node in a reducible SESE
Control Flow Graph based on the **Cooper, Harvey & Kennedy (2001)**
iterative algorithm.

# Approach
The algorithm works in **reverse post-order (RPO)** over the CFG.  
At each node it intersects the idom chains of all already-processed
predecessors.  On reducible graphs it converges in **d + 1 passes**
where *d* is the loop-nesting depth — effectively **O(n · d)**, which
is near-linear for typical programs.

## Requirements

Python ≥ 3.8 — **no third-party dependencies**.

## Usage

### Interactive mode
```
python main.py
```

### Command-line mode
```
python main.py --cfg diamond --node merge
python main.py --cfg single_loop --node loop_body --show-tree
python main.py --cfg nested_loops --node inner_body --show-tree
```

### List all available CFGs
```
python main.py --list
```

### Run tests
```
python tests.py
```

## Available CFGs

| Name | Description |
|------|-------------|
| `linear` | Straight-line sequence of 7 nodes |
| `diamond` | Simple if/else diamond |
| `nested_if` | Nested if-else |
| `single_loop` | Single while loop |
| `nested_loops` | Doubly nested while loops |
| `loop_with_break` | Loop with a mid-body branch to exit |
| `complex` | Loops + conditionals + multiple merges |
