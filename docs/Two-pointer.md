# 🧠 Two Pointers – Basic Problem Set (LeetCode + HackerRank)

Two pointers is a technique where you use two indices (pointers) moving towards or away from each other to efficiently solve problems on arrays or strings.

---

## ⚙️ Template

```python
def two_pointer(nums, target=None):
    nums.sort()  # optional for sorted-based logic
    left, right = 0, len(nums) - 1

    while left < right:
        current_sum = nums[left] + nums[right]
        if current_sum == target:
            return [nums[left], nums[right]]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 1: [Two Sum II – Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) (LeetCode 167) [Medium]

Task: Find two numbers that add up to the target.

```python
def twoSum(numbers, target):
    left, right = 0, len(numbers) - 1
    while left < right:
        total = numbers[left] + numbers[right]
        if total == target:
            return [left + 1, right + 1]
        elif total < target:
            left += 1
        else:
            right -= 1
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 2: [Move Zeroes](https://leetcode.com/problems/move-zeroes/) (LeetCode 283) [Easy]

Task: Move all zeroes to the end, maintaining order.

```python
def moveZeroes(nums):
    position = 0
    for current in range(len(nums)):
        if nums[current] != 0:
            nums[position], nums[current] = nums[current], nums[position]
            position += 1
    return nums
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 3: [Reverse String](https://leetcode.com/problems/reverse-string/) (LeetCode 344) [Easy]

Task: Reverse characters in a string in place.

```python
def reverseString(s):
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
    return s
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 4: [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) (LeetCode 125) [Easy]

Task: Check if a string reads the same backward and forward.

```python
def isPalindrome(s):
    cleaned = ''.join(ch.lower() for ch in s if ch.isalnum())
    left, right = 0, len(cleaned) - 1
    while left < right:
        if cleaned[left] != cleaned[right]:
            return False
        left += 1
        right -= 1
    return True
```

**Time Complexity:** O(n)
**Space Complexity:** O(n)

---

## 🧩 Problem 5: [Merge Sorted Arrays](https://leetcode.com/problems/merge-sorted-array/) (LeetCode 88) [Easy]

Task: Merge two sorted arrays `nums1` and `nums2` into `nums1`.

```python
def merge(nums1, m, nums2, n):
    index1, index2, insert_pos = m - 1, n - 1, m + n - 1
    while index2 >= 0:
        if index1 >= 0 and nums1[index1] > nums2[index2]:
            nums1[insert_pos] = nums1[index1]
            index1 -= 1
        else:
            nums1[insert_pos] = nums2[index2]
            index2 -= 1
        insert_pos -= 1
```

**Time Complexity:** O(m+n)
**Space Complexity:** O(1)

---

## 🧩 Problem 6: [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) (LeetCode 26) [Easy]

Task: Remove duplicates in-place from a sorted array.

```python
def removeDuplicates(nums):
    insert_pos = 1
    for current in range(1, len(nums)):
        if nums[current] != nums[current - 1]:
            nums[insert_pos] = nums[current]
            insert_pos += 1
    return insert_pos
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 7: [Squares of a Sorted Array](https://leetcode.com/problems/squares-of-a-sorted-array/) (LeetCode 977) [Easy]

Task: Return the squares of the numbers in non-decreasing order.

```python
def sortedSquares(nums):
    left, right = 0, len(nums) - 1
    result = []
    while left <= right:
        if abs(nums[left]) > abs(nums[right]):
            result.append(nums[left] ** 2)
            left += 1
        else:
            result.append(nums[right] ** 2)
            right -= 1
    return result[::-1]
```

**Time Complexity:** O(n)
**Space Complexity:** O(n)

---

## 🧩 Problem 8: [Remove Element](https://leetcode.com/problems/remove-element/) (LeetCode 27) [Easy]

Task: Remove all occurrences of `val` in-place.

```python
def removeElement(nums, val):
    insert_pos = 0
    for current in range(len(nums)):
        if nums[current] != val:
            nums[insert_pos] = nums[current]
            insert_pos += 1
    return insert_pos
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 9: [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) (LeetCode 11) [Medium]

Task: Find the maximum area between two lines.

```python
def maxArea(height):
    left, right = 0, len(height) - 1
    max_area = 0
    while left < right:
        width = right - left
        area = min(height[left], height[right]) * width
        max_area = max(max_area, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_area
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 10: [Pairs with Given Difference](https://www.hackerrank.com/challenges/pairs/problem) (HackerRank) [Medium]

Task: Count pairs with difference `k`.

```python
def pairs(k, arr):
    arr.sort()
    left, right = 0, 1
    count = 0
    while right < len(arr):
        difference = arr[right] - arr[left]
        if difference == k:
            count += 1
            right += 1
        elif difference < k:
            right += 1
        else:
            left += 1
        if left == right:
            right += 1
    return count
```

**Time Complexity:** O(n log n) due to sorting
**Space Complexity:** O(1)
