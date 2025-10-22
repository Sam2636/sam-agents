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

## 1.[Two Sum II – Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/)

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

## 2.[Move Zeroes](https://leetcode.com/problems/move-zeroes/)

Task: Move all zeroes to the end, maintaining order.

```python
def moveZeroes(nums):
    slow, fast = 0, 0
    while fast < len(nums):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1
        fast += 1
    return nums
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 3.[Reverse String](https://leetcode.com/problems/reverse-string/)

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

## 4.[Valid Palindrome](https://leetcode.com/problems/valid-palindrome/)

Task: Check if a string reads the same backward and forward.

```python
def isPalindrome(s):
    left, right = 0, len(s) - 1
    
    while left < right:
        # Skip non-alphanumeric on the left
        while left < right and not s[left].isalnum():
            left += 1
        # Skip non-alphanumeric on the right
        while left < right and not s[right].isalnum():
            right -= 1
        
        # Compare characters
        if s[left].lower() != s[right].lower():
            return False
        
        left += 1
        right -= 1
    
    return True
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 5.[Merge Sorted Arrays](https://leetcode.com/problems/merge-sorted-array/)

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

## 6.[Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) 

Task: Remove duplicates in-place from a sorted array.

```python
def removeDuplicates(nums):
    if not nums:
        return 0
    
    slow = 0  # points to last unique element
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1  # length of unique elements

```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 7.[Squares of a Sorted Array](https://leetcode.com/problems/squares-of-a-sorted-array/) 

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

## 8.[Remove Element](https://leetcode.com/problems/remove-element/)

Task: Remove all occurrences of `val` in-place.

```python
def removeElement(nums, val):
    slow = 0  # points to the position to place next non-val element
    for fast in range(len(nums)):
        if nums[fast] != val:
            nums[slow] = nums[fast]
            slow += 1
    return slow  # new length of the array without val

```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 9.[Container With Most Water](https://leetcode.com/problems/container-with-most-water/) 

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

## 10.[Pairs with Given Difference](https://www.hackerrank.com/challenges/pairs/problem) 

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
