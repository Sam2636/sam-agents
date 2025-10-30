# 🧠 Sliding Window Problem Set (LeetCode)

Sliding window is a technique used for problems involving contiguous subarrays or substrings, enabling optimized O(n) solutions in many cases.

## NOTES [SLIDING WINDOW](https://www.geeksforgeeks.org/dsa/window-sliding-technique/)
---

## ⚙️ Template

```python
def sliding_window(arr, k):
    window_sum = 0
    for i in range(len(arr)):
        window_sum += arr[i]  # Add current element
        if i >= k - 1:
            # Process current window
            print(window_sum)
            window_sum -= arr[i - k + 1]  # Remove element going out of window
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 1: [Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/)

```python
def findMaxAverage(nums, k):
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum / k
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 2: [Number of Subarrays of Size K and Average Greater Than or Equal to Threshold](https://leetcode.com/problems/number-of-subarrays-of-size-k-and-average-greater-than-or-equal-to-threshold/)

```python
def numOfSubarrays(arr, k, threshold):
    window_sum = sum(arr[:k])
    count = 1 if window_sum / k >= threshold else 0
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]
        if window_sum / k >= threshold:
            count += 1
    return count
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 3: [Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/)

```python
from collections import Counter

def findAnagrams(s, p):
    p_count = Counter(p)
    s_count = Counter()
    res = []
    k = len(p)

    for i in range(len(s)):
        s_count[s[i]] += 1
        if i >= k:
            if s_count[s[i - k]] == 1:
                del s_count[s[i - k]]
            else:
                s_count[s[i - k]] -= 1
        if s_count == p_count:
            res.append(i - k + 1)
    return res
```

**Time Complexity:** O(n)
**Space Complexity:** O(26) ~ O(1)

---

## 🧩 Problem 4: [Permutation in String](https://leetcode.com/problems/permutation-in-string/)

```python
from collections import Counter

def checkInclusion(s1, s2):
    k = len(s1)
    s1_count = Counter(s1)
    s2_count = Counter()
    
    for i in range(len(s2)):
        s2_count[s2[i]] += 1
        if i >= k:
            if s2_count[s2[i - k]] == 1:
                del s2_count[s2[i - k]]
            else:
                s2_count[s2[i - k]] -= 1
        if s1_count == s2_count:
            return True
    return False
```

**Time Complexity:** O(n)
**Space Complexity:** O(26) ~ O(1)

---

## 🧩 Problem 5: [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/)

```python
from collections import deque

def maxSlidingWindow(nums, k):
    q = deque()  # stores indices
    res = []
    for i, num in enumerate(nums):
        while q and q[0] <= i - k:
            q.popleft()
        while q and nums[q[-1]] < num:
            q.pop()
        q.append(i)
        if i >= k - 1:
            res.append(nums[q[0]])
    return res
```

**Time Complexity:** O(n)
**Space Complexity:** O(k)

---

## 🧩 Problem 6: [Maximum Points You Can Obtain from Cards](https://leetcode.com/problems/maximum-points-you-can-obtain-from-cards/)

```python
def maxScore(cardPoints, k):
    n = len(cardPoints)
    total = sum(cardPoints[:k])
    max_total = total
    for i in range(k):
        total += cardPoints[-(i+1)] - cardPoints[k-i-1]
        max_total = max(max_total, total)
    return max_total
```

**Time Complexity:** O(k)
**Space Complexity:** O(1)

---

## 🧩 Problem 7: [Check If a String Contains All Binary Codes of Size K](https://leetcode.com/problems/check-if-a-string-contains-all-binary-codes-of-size-k/)

```python
def hasAllCodes(s, k):
    needed = set(range(1 << k))
    current = 0
    for i, ch in enumerate(s):
        current = ((current << 1) & ((1 << k) - 1)) | int(ch)
        if i >= k - 1:
            needed.discard(current)
    return not needed
```

**Time Complexity:** O(n)
**Space Complexity:** O(2^k)

---

## 🧩 Problem 8: [Substrings of Size Three with Distinct Characters](https://leetcode.com/problems/substrings-of-size-three-with-distinct-characters/)

```python
def countGoodSubstrings(s):
    count = 0
    for i in range(len(s) - 2):
        if len(set(s[i:i+3])) == 3:
            count += 1
    return count
```

**Time Complexity:** O(n)
**Space Complexity:** O(1)

---

## 🧩 Problem 9: [Maximum Sum of Distinct Subarrays With Length K](https://leetcode.com/problems/maximum-sum-of-distinct-subarrays-with-length-k/)

```python
def maximumSubarraySum(nums, k):
    window_sum = 0
    window_count = {}
    max_sum = 0

    for i in range(len(nums)):
        window_count[nums[i]] = window_count.get(nums[i], 0) + 1
        window_sum += nums[i]

        if i >= k:
            window_count[nums[i - k]] -= 1
            if window_count[nums[i - k]] == 0:
                del window_count[nums[i - k]]
            window_sum -= nums[i - k]

        if i >= k - 1 and len(window_count) == k:
            max_sum = max(max_sum, window_sum)
    return max_sum
```

**Time Complexity:** O(n)
**Space Complexity:** O(k)

---

## 🧩 Problem 10: [Sliding Subarray Beauty](https://leetcode.com/problems/sliding-subarray-beauty/)

```python
def getSubarrayBeauty(nums, k, x):
    from sortedcontainers import SortedList
    sl = SortedList()
    res = []
    for i, num in enumerate(nums):
        sl.add(num)
        if i >= k:
            sl.remove(nums[i - k])
        if i >= k - 1:
            negatives = [n for n in sl if n < 0]
            res.append(negatives[x-1] if len(negatives) >= x else 0)
    return res
```

**Time Complexity:** O(n log k)
**Space Complexity:** O(k)
