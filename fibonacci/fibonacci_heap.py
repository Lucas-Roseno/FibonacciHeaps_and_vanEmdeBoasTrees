"""
Fibonacci Heap implementation in Python following the pseudocode and design from
Cormen et al., Chapter 19 (Fibonacci Heaps).

This module implements the operations described in the book:
- MAKE-FIB-HEAP  -> FibonacciHeap() constructor
- FIB-HEAP-INSERT -> insert(key)
- FIB-HEAP-MINIMUM -> minimum()
- FIB-HEAP-UNION -> union(other)
- FIB-HEAP-EXTRACT-MIN -> extract_min()
- FIB-HEAP-DECREASE-KEY -> decrease_key(node, new_key)
- FIB-HEAP-DELETE -> delete(node)

Nodes returned by insert(...) should be kept by the caller if they need to
invoke decrease_key or delete on specific elements.

This implementation aims to follow the structure, invariants and helper
procedures (CONSOLIDATE, CUT, CASCADING-CUT, FIB-HEAP-LINK) from the book,
with Pythonic adjustments.

Note: This is an educational implementation prioritizing clarity and
conformance to the book over maximal micro-optimizations.
"""

from __future__ import annotations
from typing import Optional, Any, List
import math


class Node:
    __slots__ = (
        "key",
        "degree",
        "mark",
        "parent",
        "child",
        "left",
        "right",
        "payload",
    )

    def __init__(self, key: Any, payload: Any = None):
        self.key = key
        self.degree = 0
        self.mark = False
        self.parent: Optional[Node] = None
        self.child: Optional[Node] = None
        # For circular doubly linked lists. Single node points to itself.
        self.left: Node = self
        self.right: Node = self
        # Optional user payload (e.g., pointer to application object)
        self.payload = payload

    def __repr__(self) -> str:
        return f"Node(key={self.key}, degree={self.degree}, mark={self.mark})"


class FibonacciHeap:
    def __init__(self):
        # pointer to min node in the root list
        self.min: Optional[Node] = None
        self.n: int = 0

    # -------------------- low-level circular-list helpers --------------------
    @staticmethod
    def _insert_into_root_list(root: Optional[Node], node: Node) -> Node:
        """Insert node into circular doubly linked list 'root'.
        Returns new root (not necessarily min).
        If root is None, node becomes the single element circular list.
        """
        if root is None:
            node.left = node.right = node
            return node
        # insert node to the left of root
        node.left = root.left
        node.right = root
        root.left.right = node
        root.left = node
        return root

    @staticmethod
    def _remove_from_list(node: Node) -> None:
        """Remove 'node' from its circular list. If it is single, leaves
        node.left/node.right pointing to itself (caller should set parent/child
        accordingly).
        """
        if node.right is node:
            # single element
            return
        node.left.right = node.right
        node.right.left = node.left
        node.left = node.right = node

    # -------------------- public interface --------------------
    def insert(self, key: Any, payload: Any = None) -> Node:
        """Insert a key (and optional payload) into the heap. Returns the Node.

        Time: O(1) amortized (as in Cormen)
        """
        x = Node(key, payload)
        # add x to root list
        self.min = self._insert_into_root_list(self.min, x)
        if self.min is None or x.key < self.min.key:
            self.min = x
        self.n += 1
        return x

    def minimum(self) -> Optional[Node]:
        """Return the node with minimum key (or None if heap empty). O(1)."""
        return self.min

    def union(self, other: "FibonacciHeap") -> "FibonacciHeap":
        """Union two Fibonacci heaps in O(1) (amortized). The two input heaps
        are destroyed conceptually: their root lists are concatenated and a
        new heap is returned.
        """
        H = FibonacciHeap()
        H.min = self.min
        # concatenate root lists
        if H.min is None:
            H.min = other.min
        elif other.min is not None:
            # splice the two circular lists
            a = H.min.left
            b = other.min.left
            a.right = other.min
            other.min.left = a
            b.right = H.min
            H.min.left = b
            # choose min pointer
            if other.min.key < H.min.key:
                H.min = other.min
        H.n = self.n + other.n
        # invalidate the two heaps (optional) -- for safety we clear them
        self.min = None
        self.n = 0
        other.min = None
        other.n = 0
        return H

    # -------------------- extract-min and helpers --------------------
    def extract_min(self) -> Optional[Node]:
        z = self.min
        if z is not None:
            # For each child of z, add to root list
            children = []
            child = z.child
            if child is not None:
                # gather children (they are in a circular list)
                curr = child
                while True:
                    children.append(curr)
                    curr = curr.right
                    if curr is child:
                        break
                # for each child: remove parent link and add to root list
                for c in children:
                    c.parent = None
                    # remove c from its sibling list and insert into root list
                    FibonacciHeap._remove_from_list(c)
                    self.min = self._insert_into_root_list(self.min, c)
            # remove z from root list
            if z.right is z:
                # z was the only node in root list
                self.min = None
            else:
                # remove z and set min to some other root temporarily
                z.left.right = z.right
                z.right.left = z.left
                self.min = z.right
                # consolidate will fix self.min
            self.n -= 1
            if self.min is not None:
                self._consolidate()
        return z

    def _consolidate(self) -> None:
        # upper bound on degree: floor(log_phi(n)) where phi ~=1.618.
        # using log2 is safe; we add some slack.
        if self.n <= 0:
            return
        max_deg = int(math.log(self.n, 2)) + 2
        A: List[Optional[Node]] = [None] * (max_deg + 1)

        # collect roots into a list (to iterate safely while mutating root list)
        roots: List[Node] = []
        curr = self.min
        if curr is not None:
            while True:
                roots.append(curr)
                curr = curr.right
                if curr is self.min:
                    break

        for w in roots:
            x = w
            d = x.degree
            # ensure A big enough
            while d >= len(A):
                A.extend([None] * len(A))
            while A[d] is not None:
                y = A[d]
                if x.key > y.key:
                    x, y = y, x
                # link y under x
                self._heap_link(y, x)
                A[d] = None
                d += 1
            A[d] = x

        # rebuild root list and find new min
        self.min = None
        for entry in A:
            if entry is not None:
                # isolate entry into single-node circular list
                entry.left = entry.right = entry
                if self.min is None:
                    self.min = entry
                else:
                    # insert into root list
                    self.min = self._insert_into_root_list(self.min, entry)
                    if entry.key < self.min.key:
                        self.min = entry

    def _heap_link(self, y: Node, x: Node) -> None:
        """Make y a child of x. Remove y from root list; increment x.degree
        and clear y.mark. This follows FIB-HEAP-LINK in Cormen.
        """
        # remove y from root list
        FibonacciHeap._remove_from_list(y)
        # make y a child of x
        y.parent = x
        if x.child is None:
            y.left = y.right = y
            x.child = y
        else:
            # insert y into child's circular list
            child = x.child
            y.left = child.left
            y.right = child
            child.left.right = y
            child.left = y
        x.degree += 1
        y.mark = False

    # -------------------- decrease-key, cut, cascading-cut --------------------
    def decrease_key(self, x: Node, k: Any) -> None:
        if k > x.key:
            raise ValueError("new key is greater than current key")
        x.key = k
        y = x.parent
        if y is not None and x.key < y.key:
            self._cut(x, y)
            self._cascading_cut(y)
        if self.min is None or x.key < self.min.key:
            self.min = x

    def _cut(self, x: Node, y: Node) -> None:
        # remove x from y's child list
        if y.child is x:
            # if x is the only child
            if x.right is x:
                y.child = None
            else:
                y.child = x.right
        FibonacciHeap._remove_from_list(x)
        y.degree -= 1
        # add x to root list
        x.parent = None
        x.left = x.right = x
        self.min = self._insert_into_root_list(self.min, x)
        x.mark = False

    def _cascading_cut(self, y: Node) -> None:
        z = y.parent
        if z is not None:
            if not y.mark:
                y.mark = True
            else:
                self._cut(y, z)
                self._cascading_cut(z)

    # -------------------- delete --------------------
    def delete(self, x: Node) -> None:
        # decrease key to -infinity, then extract-min
        self.decrease_key(x, float("-inf"))
        self.extract_min()


# -------------------- optional small demo when run as script --------------------
if __name__ == "__main__":
    # small usage demo
    H = FibonacciHeap()
    a = H.insert(7)
    b = H.insert(3)
    c = H.insert(17)
    print("min:", H.minimum())
    z = H.extract_min()
    print("extracted:", z)
    print("min after extract:", H.minimum())
    H.decrease_key(c, 1)
    print("min after decrease-key:", H.minimum())
    H.delete(c)
    print("min after delete:", H.minimum())
