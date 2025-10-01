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
