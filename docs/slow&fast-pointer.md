# 🐢🐇 Slow and Fast Pointer Pattern

This document covers **7 core problems** that use the **slow and fast pointer technique**, primarily for **linked lists** and **cycle detection** problems.

Each solution includes the **approach**, **intuition**, and **code** with meaningful variable names.

---

## 1. [141. Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/)

**Intuition:**
Use two pointers — slow moves one step, fast moves two. If they ever meet, a cycle exists.

```python
class Solution:
    def hasCycle(self, head):
        slow_pointer = head
        fast_pointer = head
        while fast_pointer and fast_pointer.next:
            slow_pointer = slow_pointer.next
            fast_pointer = fast_pointer.next.next
            if slow_pointer == fast_pointer:
                return True
        return False
```

---

## 2. [142. Linked List Cycle II](https://leetcode.com/problems/linked-list-cycle-ii/)

**Intuition:**
After detecting a cycle, reset one pointer to the head and move both at the same speed — they meet at the cycle start.

```python
class Solution:
    def detectCycle(self, head):
        slow_pointer = head
        fast_pointer = head
        while fast_pointer and fast_pointer.next:
            slow_pointer = slow_pointer.next
            fast_pointer = fast_pointer.next.next
            if slow_pointer == fast_pointer:
                break
        else:
            return None
        slow_pointer = head
        while slow_pointer != fast_pointer:
            slow_pointer = slow_pointer.next
            fast_pointer = fast_pointer.next
        return slow_pointer
```

---

## 3. [202. Happy Number](https://leetcode.com/problems/happy-number/)

**Intuition:**
Use Floyd’s cycle detection to identify loops in the sum-of-squares process.

```python
def get_next(num):
    return sum(int(digit) ** 2 for digit in str(num))

class Solution:
    def isHappy(self, n):
        slow_pointer = n
        fast_pointer = get_next(n)
        while fast_pointer != 1 and slow_pointer != fast_pointer:
            slow_pointer = get_next(slow_pointer)
            fast_pointer = get_next(get_next(fast_pointer))
        return fast_pointer == 1
```

---

## 4. [876. Middle of the Linked List](https://leetcode.com/problems/middle-of-the-linked-list/)

**Intuition:**
Fast pointer moves two nodes while slow moves one. When fast reaches the end, slow will be in the middle.

```python
class Solution:
    def middleNode(self, head):
        slow_pointer = head
        fast_pointer = head
        while fast_pointer and fast_pointer.next:
            slow_pointer = slow_pointer.next
            fast_pointer = fast_pointer.next.next
        return slow_pointer
```

---

## 5. [234. Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/)

**Intuition:**
Use fast and slow pointers to find the middle, reverse the second half, and compare both halves.

```python
class Solution:
    def isPalindrome(self, head):
        def reverse_list(node):
            prev = None
            while node:
                next_node = node.next
                node.next = prev
                prev = node
                node = next_node
            return prev

        slow_pointer = fast_pointer = head
        while fast_pointer and fast_pointer.next:
            slow_pointer = slow_pointer.next
            fast_pointer = fast_pointer.next.next

        second_half = reverse_list(slow_pointer)
        first_half = head
        while second_half:
            if first_half.val != second_half.val:
                return False
            first_half = first_half.next
            second_half = second_half.next
        return True
```

---

## 6. [19. Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)

**Intuition:**
Maintain a gap of `n` between fast and slow pointers. When fast reaches the end, slow will be just before the node to delete.

```python
class Solution:
    def removeNthFromEnd(self, head, n):
        dummy = ListNode(0, head)
        slow_pointer = dummy
        fast_pointer = dummy

        for _ in range(n + 1):
            fast_pointer = fast_pointer.next

        while fast_pointer:
            slow_pointer = slow_pointer.next
            fast_pointer = fast_pointer.next

        slow_pointer.next = slow_pointer.next.next
        return dummy.next
```

---

## 7. [143. Reorder List](https://leetcode.com/problems/reorder-list/)

**Intuition:**
Split list into two halves, reverse the second, then merge alternately.

```python
class Solution:
    def reorderList(self, head):
        if not head:
            return

        # Step 1: Find middle
        slow_pointer, fast_pointer = head, head
        while fast_pointer and fast_pointer.next:
            slow_pointer = slow_pointer.next
            fast_pointer = fast_pointer.next.next

        # Step 2: Reverse second half
        prev, curr = None, slow_pointer
        while curr:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node

        # Step 3: Merge two halves
        first, second = head, prev
        while second.next:
            temp1, temp2 = first.next, second.next
            first.next = second
            second.next = temp1
            first, second = temp1, temp2
```

---

✅ **Summary of Key Uses**

| Purpose          | Example Problems |
| ---------------- | ---------------- |
| Detect cycle     | 141, 142, 202    |
| Find middle      | 876              |
| Split list       | 143, 234         |
| Remove from end  | 19               |
| Reverse or merge | 143, 234         |
