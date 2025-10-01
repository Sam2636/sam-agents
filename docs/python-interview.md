---

# **Python Interview Questions and Answers (Beginner → Advanced)**

---

## **Beginner (Basics, Data Types, Loops, Functions)**

1. **What is Python?**
   Python is a high-level, interpreted language known for its simplicity and readability. It supports multiple paradigms like procedural, object-oriented, and functional programming.

2. **What are Python’s key features?**
   Python is interpreted, dynamically typed, and object-oriented. It has a rich standard library and allows easy integration with other languages and tools.

3. **What is PEP 8?**
   PEP 8 is Python’s style guide that defines conventions for writing readable and consistent code. Following it improves maintainability and collaboration.

4. **Difference between Python 2 and Python 3?**
   Python 3 uses `print()` as a function, supports Unicode by default, and division returns a float. Python 2 uses `print` as a statement and integer division truncates results.

5. **What are Python’s data types?**
   Python has types like `int`, `float`, `str`, `list`, `tuple`, `set`, `dict`, `bool`, and `NoneType`. Each type helps store and manipulate specific kinds of data.

6. **Mutable vs Immutable types?**
   Mutable types (`list`, `dict`, `set`) can be changed after creation. Immutable types (`tuple`, `str`, `int`, `float`) cannot, affecting how they behave in memory.

7. **What is Python’s indentation rule?**
   Python uses indentation to define code blocks instead of braces `{}`. Proper indentation is mandatory to avoid syntax errors.

8. **What are comments in Python?**
   Single-line comments use `#`. Multi-line comments use triple quotes `'''` or `"""`. They are ignored during execution.

9. **What are Python’s built-in functions for collections?**
   Common ones include `len()`, `sum()`, `max()`, `min()`, `sorted()`, and `reversed()`. These simplify operations on lists, sets, tuples, and dictionaries.

10. **Difference between list and tuple?**
    Lists are mutable and slower, while tuples are immutable, faster, and use less memory. Use tuples for fixed data and lists for changeable data.

11. **Difference between list and set?**
    Lists are ordered and allow duplicates, sets are unordered and store only unique elements. Sets are efficient for membership tests.

12. **Difference between `==` and `is`?**
    `==` checks **value equality**, while `is` checks **object identity** in memory. Use `is` to compare object references.

13. **How to remove duplicates from a list?**
    Convert to a set and back: `unique = list(set(lst))`. This removes duplicates but may reorder elements.

14. **How to iterate over a list?**
    Use `for item in list` for values, or `for i in range(len(list))` for indices. `enumerate()` is preferred for index + value.

15. **What is a function in Python?**
    A function is a reusable block of code that performs a task. It can accept parameters and return values using `return`.

---

## **Intermediate (OOP, Modules, File Handling, Error Handling)**

16. **What is `*args` and `**kwargs`?**
    `*args` passes a variable number of positional arguments, while `**kwargs` passes variable keyword arguments. They make functions flexible.

17. **What is a lambda function?**
    Lambda is an anonymous, single-line function used for simple operations. Example: `square = lambda x: x**2`.

18. **Difference between `@staticmethod` and `@classmethod`?**
    `@staticmethod` does not access class or instance data, while `@classmethod` takes the class itself as the first parameter. Both decorate methods differently.

19. **What is inheritance?**
    Inheritance allows a class to derive properties and methods from another class. It promotes code reuse and hierarchy.

20. **What is polymorphism?**
    Polymorphism allows different objects to respond to the same method call in different ways. It includes method overriding and operator overloading.

21. **What is encapsulation?**
    Encapsulation hides internal object details using private variables. Access is provided via getter/setter methods.

22. **Difference between class variable and instance variable?**
    Class variables are shared across instances; instance variables are unique per object. Both are used for storing data in classes.

23. **What is `super()`?**
    `super()` allows calling parent class methods from a child class. It is commonly used in constructors to initialize inherited attributes.

24. **What are decorators?**
    Decorators modify the behavior of a function or class without changing its code. They are commonly used for logging, validation, or access control.

25. **How to read and write files?**
    Use `with open('file.txt', 'r') as f:` to read and `with open('file.txt', 'w') as f:` to write. `with` ensures files are properly closed.

26. **Difference between `read()`, `readline()`, `readlines()`?**
    `read()` reads the entire file, `readline()` reads one line, `readlines()` returns a list of lines. Use based on memory and processing needs.

27. **Difference between `import module` and `from module import function`?**
    `import module` requires prefixing with `module.func()`, `from module import func` allows direct access to `func()`.

28. **What is `__name__ == "__main__"`?**
    It checks whether the script is executed directly or imported as a module. Code under this runs only when the file is executed directly.

29. **How to handle exceptions?**
    Use `try-except` blocks to catch errors. Example:

```python
try: x=1/0
except ZeroDivisionError: print("Cannot divide by zero")
```

30. **Difference between `finally` and `else` in try-except?**
    `finally` executes always, regardless of errors. `else` executes only if no exception occurs.

---

## **Advanced (Advanced OOP, Iterators, Generators, Concurrency, Modules)**

31. **What is Python GIL?**
    The Global Interpreter Lock allows only one thread to execute Python bytecode at a time. It limits CPU-bound multi-threading.

32. **Difference between multithreading and multiprocessing?**
    Threading runs multiple threads in shared memory, limited by GIL. Multiprocessing uses separate processes for true parallelism.

33. **What is a generator?**
    A generator is an iterator that yields values one at a time using `yield`. It is memory-efficient for large datasets.

34. **Difference between `yield` and `return`?**
    `return` sends a value and exits the function. `yield` sends a value but pauses function execution, resuming later.

35. **What are iterators?**
    Iterators implement `__iter__()` and `__next__()` methods to traverse collections. Generators are a special kind of iterator.

36. **Difference between deep copy and shallow copy?**
    Shallow copy copies the object structure but references nested objects. Deep copy duplicates the object and all nested elements independently.

37. **What is a context manager (`with` statement)?**
    `with` ensures resources are properly managed (like files). It automatically closes files or releases resources after use.

38. **What are comprehensions?**
    Python comprehensions provide concise syntax to create lists, sets, and dictionaries. Example: `[x**2 for x in range(5)]`.

39. **Difference between `is` and `==`?**
    `is` checks if two objects are identical in memory, `==` checks if values are equal. Use `is` for object identity.

40. **Difference between `del` and `remove()`?**
    `del lst[0]` deletes by index, `lst.remove(val)` deletes by value. `del` can also remove variables entirely.

41. **What is a Python module?**
    A module is a file containing Python code (functions, classes, variables) that can be reused in other programs. Modules improve code organization.

42. **What is a package?**
    A package is a collection of modules organized in directories with `__init__.py`. Packages allow modular project structures.

43. **Popular Python libraries for data?**
    `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`, `requests`, `json`. They cover computation, visualization, and web access.

44. **Difference between Python array and list?**
    Lists can hold mixed data types; arrays (from `array` module or `numpy`) hold elements of the same type and are more memory efficient.

45. **How to manage dependencies in Python?**
    Use `pip` for installing packages, and `requirements.txt` to track dependencies. Virtual environments isolate project packages.

46. **What is Python’s `itertools` module?**
    `itertools` provides efficient iterators for combinations, permutations, and Cartesian products. Useful for algorithmic tasks.

47. **What is Python’s `functools` module?**
    `functools` provides higher-order functions like `reduce()`, `partial()`, and decorators. It simplifies functional programming tasks.

48. **How to profile Python code?**
    Use the `cProfile` module to measure execution time and function calls. Profiling identifies performance bottlenecks.

49. **What is monkey patching?**
    Monkey patching modifies or extends modules/classes at runtime. It can fix bugs or add features without modifying original code.

50. **Difference between Python threads and asyncio?**
    Threads run concurrently with shared memory but limited by GIL. `asyncio` uses cooperative multitasking with `async/await` for I/O-bound tasks.

---

This **categorization makes it easier** to target questions based on skill level:

* **Beginner:** Basics, data types, loops, functions
* **Intermediate:** OOP, file handling, error handling, modules
* **Advanced:** Iterators, generators, concurrency, performance, advanced OOP

---
