# LeetCode Patterns - Base Template

This is a base template for documenting all **8 common LeetCode patterns**. You can fill in examples, Python starter code, scenarios, and notes for each pattern.

---

## 1. Two Pointers

**Description:**

* Compare or find pairs from two ends of an array or string.

**Python Template:**

```python
left, right = 0, len(arr) - 1
while left < right:
    # Your logic here
    left += 1
    right -= 1
```

---

## 2. Sliding Window

**Description:**

* Maintain a window of size k to track information over contiguous subarrays or substrings.

**Python Template:**

```python
window_sum = sum(arr[:k])
for i in range(len(arr) - k):
    window_sum = window_sum - arr[i] + arr[i+k]
    # Your logic here
```

---

## 3. Fast & Slow Pointers

**Description:**

* Two pointers moving at different speeds to detect cycles or find middle elements.

**Python Template:**

```python
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow == fast:
        # Cycle detected
```

---

## 4. DFS / Backtracking

**Description:**

* Explore all paths recursively or iteratively, useful for generating combinations/permutations.

**Python Template:**

```python
def dfs(node, path):
    # Base case
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(neighbor, path)
```

---

## 5. BFS / Queue

**Description:**

* Explore nodes level by level using a queue.

**Python Template:**

```python
from collections import deque
queue = deque([start])
while queue:
    node = queue.popleft()
    for neighbor in graph[node]:
        queue.append(neighbor)
```

---

## 6. Stack

**Description:**

* LIFO data structure, useful for reversals, parentheses matching, and DFS iterative implementation.

**Python Template:**

```python
stack = []
stack.append(item)
while stack:
    item = stack.pop()
    # Your logic here
```

---

## 7. Queue

**Description:**

* FIFO data structure, useful for BFS, scheduling, or streaming problems.

**Python Template:**

```python
from collections import deque
queue = deque()
queue.append(item)
while queue:
    item = queue.popleft()
    # Your logic here
```

---

## 8. Binary Search

**Description:**

* Efficiently search in sorted arrays or answer space by halving the search range.

**Python Template:**

```python
left, right = 0, len(arr) - 1
while left <= right:
    mid = (left + right) // 2
    if arr[mid] == target:
        break
    elif arr[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
```

## 9. Linked List Pattern

**Description:**
Manipulating nodes, reversing, merging, detecting cycles.

# Reverse Linked List

    ```
    prev, curr = None, head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev
    ```

## 10. Tree Traversal (DFS & BFS)

Binary tree traversals are fundamental patterns for solving tree problems.

DFS (Depth-First Traversals)
1. Inorder Traversal (Left → Root → Right)

    ```
    def inorder(root):
        if not root: return
        inorder(root.left)
        print(root.val)
        inorder(root.right)
    ```

2. Preorder Traversal (Root → Left → Right)

    ```
    def preorder(root):
        if not root: return
        print(root.val)
        preorder(root.left)
        preorder(root.right)
    ```

3. Postorder Traversal (Left → Right → Root)

    ```
    def postorder(root):
        if not root: return
        postorder(root.left)
        postorder(root.right)
        print(root.val)
    ```

4. BFS (Level Order Traversal)

    ```
    from collections import deque

    def bfs(root):
        if not root: return
        queue = deque([root])
        while queue:
            node = queue.popleft()
            print(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    ```

🔑 When to use what?

Inorder → Sorted output for BSTs.

Preorder → Useful for copying tree / serialization.

Postorder → Useful for deleting tree / bottom-up calculations.

BFS → Best for shortest path, level-wise problems.