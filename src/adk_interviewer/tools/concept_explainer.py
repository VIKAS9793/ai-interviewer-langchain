"""
Concept Explainer Tool for Study Mode.

Provides structured explanations of CS concepts with examples,
complexity analysis, and visual representations.
"""

from typing import Literal


# Core concept library
CONCEPTS = {
    # Data Structures
    "arrays": {
        "definition": "Contiguous memory block storing elements of same type with O(1) index access.",
        "time_complexity": {
            "access": "O(1)",
            "search": "O(n)",
            "insertion": "O(n) - worst case (shift elements)",
            "deletion": "O(n) - worst case (shift elements)"
        },
        "use_cases": [
            "Fixed-size collections",
            "Fast random access needed",
            "Memory-efficient storage"
        ],
        "pitfalls": [
            "Fixed size (no dynamic resize)",
            "Expensive insertions/deletions in middle",
            "Cache-friendly but inflexible"
        ],
        "example": """
# Array operations in Python (list is dynamic array)
arr = [1, 2, 3, 4, 5]

# O(1) access
value = arr[2]  # 3

# O(n) search
index = arr.index(4)  # 3

# O(n) insertion (worst case - at beginning)
arr.insert(0, 0)  # [0, 1, 2, 3, 4, 5]
"""
    },
    
    "binary_search_trees": {
        "definition": "Tree where each node has ≤2 children, left < parent < right. Enables O(log n) operations when balanced.",
        "time_complexity": {
            "search": "O(log n) avg, O(n) worst (unbalanced)",
            "insertion": "O(log n) avg, O(n) worst",
            "deletion": "O(log n) avg, O(n) worst",
            "traversal": "O(n)"
        },
        "use_cases": [
            "Sorted data with frequent insertions/deletions",
            "Range queries",
            "Order statistics (kth smallest)"
        ],
        "pitfalls": [
            "Can degrade to linked list if unbalanced",
            "Use AVL/Red-Black trees for guaranteed balance",
            "Recursion overhead for deep trees"
        ],
        "example": """
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def search_bst(root: TreeNode, target: int) -> TreeNode:
    # O(log n) average case
    if not root or root.val == target:
        return root
    
    if target < root.val:
        return search_bst(root.left, target)
    else:
        return search_bst(root.right, target)
"""
    },
    
    "hash_maps": {
        "definition": "Key-value store using hash function to map keys to array indices. Average O(1) operations.",
        "time_complexity": {
            "access": "O(1) avg, O(n) worst (hash collisions)",
            "insertion": "O(1) avg, O(n) worst",
            "deletion": "O(1) avg, O(n) worst",
            "search": "O(1) avg, O(n) worst"
        },
        "use_cases": [
            "Fast lookup by key",
            "Frequency counting",
            "Caching/memoization"
        ],
        "pitfalls": [
            "No ordering guarantees",
            "Hash collisions degrade performance",
            "Memory overhead for hash table"
        ],
        "example": """
# Hash map in Python (dict)
freq = {}

# O(1) insertion/update
for char in "hello":
    freq[char] = freq.get(char, 0) + 1

# O(1) lookup
h_count = freq.get('h', 0)  # 1

# Result: {'h': 1, 'e': 1, 'l': 2, 'o': 1}
"""
    },
    
    "graphs": {
        "definition": "Nodes (vertices) connected by edges. Can be directed/undirected, weighted/unweighted.",
        "time_complexity": {
            "adjacency_list_space": "O(V + E)",
            "adjacency_matrix_space": "O(V²)",
            "bfs_dfs": "O(V + E)",
            "dijkstra": "O((V + E) log V) with min-heap"
        },
        "use_cases": [
            "Social networks",
            "Maps/navigation",
            "Dependency resolution"
        ],
        "pitfalls": [
            "Choose right representation (list vs matrix)",
            "Handle cycles in DFS/BFS",
            "Consider directed vs undirected semantics"
        ],
        "example": """
from collections import defaultdict, deque

# Adjacency list representation
graph = defaultdict(list)
graph[1] = [2, 3]
graph[2] = [4]
graph[3] = [4]

# BFS traversal - O(V + E)
def bfs(graph, start):
    visited = set()
    queue = deque([start])
    
    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            queue.extend(graph[node])
    
    return visited
"""
    },
}

# Algorithm concepts
ALGORITHMS = {
    "binary_search": {
        "definition": "Divide-and-conquer search on sorted array. Eliminates half of search space each iteration.",
        "time_complexity": "O(log n)",
        "space_complexity": "O(1) iterative, O(log n) recursive (call stack)",
        "prerequisites": "Array must be sorted",
        "use_cases": [
            "Search in sorted data",
            "Finding boundaries/ranges",
            "Optimization problems (binary search on answer)"
        ],
        "pitfalls": [
            "Integer overflow in mid calculation: use left + (right - left) // 2",
            "Off-by-one errors in boundaries",
            "Forgetting to handle duplicates"
        ],
        "example": """
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2  # Avoid overflow
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Not found
"""
    },
    
    "dynamic_programming": {
        "definition": "Optimization technique solving problems by breaking into overlapping subproblems. Stores results to avoid recomputation.",
        "approaches": {
            "top_down": "Recursion + memoization",
            "bottom_up": "Iterative table filling"
        },
        "time_complexity": "Typically O(n²) or O(n×m) depending on subproblem count",
        "use_cases": [
            "Optimization problems (min/max)",
            "Counting problems",
            "Decision problems (yes/no)"
        ],
        "pitfalls": [
            "Identify overlapping subproblems",
            "Define state correctly",
            "Watch space complexity (can optimize with rolling array)"
        ],
        "example": """
# Fibonacci with DP (bottom-up)
def fib_dp(n):
    if n <= 1:
        return n
    
    # O(n) time, O(1) space (rolling variables)
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    
    return curr

# Fibonacci with memoization (top-down)
def fib_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]
"""
    },
}


def explain_concept(
    topic: str,
    depth: Literal["quick", "standard", "deep"],
    tool_context) -> str:
    """
    Explain a CS concept with examples and complexity analysis.
    
    Args:
        topic: Concept name (e.g., "binary_search_trees", "dynamic_programming")
        depth: Explanation depth - quick (overview), standard (detailed), deep (comprehensive)
        tool_context: ADK tool execution context
        
    Returns:
        Structured explanation with definition, complexity, examples, pitfalls
    """
    # Normalize topic
    topic_key = topic.lower().replace(" ", "_")
    
    # Search concept library
    concept = CONCEPTS.get(topic_key) or ALGORITHMS.get(topic_key)
    
    if not concept:
        # Concept not found - provide helpful response
        available = list(CONCEPTS.keys()) + list(ALGORITHMS.keys())
        return f"""❌ Concept '{topic}' not found in library.

📚 Available topics:
Data Structures: {', '.join(CONCEPTS.keys())}
Algorithms: {', '.join(ALGORITHMS.keys())}

💡 Try: "Explain binary_search_trees" or "Explain dynamic_programming"
"""
    
    # Build explanation based on depth
    if depth == "quick":
        explanation = f"""# {topic.replace('_', ' ').title()}

**Definition:** {concept.get('definition', 'N/A')}

**Key Point:** {concept.get('use_cases', ['General purpose'])[0]}
"""
    
    elif depth == "deep":
        # Comprehensive explanation with all details
        parts = [f"# {topic.replace('_', ' ').title()}\n"]
        
        parts.append(f"## Definition\n{concept['definition']}\n")
        
        if 'time_complexity' in concept:
            parts.append("## Time Complexity")
            if isinstance(concept['time_complexity'], dict):
                for op, complexity in concept['time_complexity'].items():
                    parts.append(f"- **{op.replace('_', ' ').title()}:** {complexity}")
            else:
                parts.append(f"- {concept['time_complexity']}")
            parts.append("")
        
        if 'space_complexity' in concept:
            parts.append(f"## Space Complexity\n{concept['space_complexity']}\n")
        
        if 'use_cases' in concept:
            parts.append("## Use Cases")
            for uc in concept['use_cases']:
                parts.append(f"- {uc}")
            parts.append("")
        
        if 'pitfalls' in concept:
            parts.append("## ⚠️ Common Pitfalls")
            for pf in concept['pitfalls']:
                parts.append(f"- {pf}")
            parts.append("")
        
        if 'example' in concept:
            parts.append(f"## Code Example\n```python{concept['example']}```\n")
        
        if 'prerequisites' in concept:
            parts.append(f"## Prerequisites\n{concept['prerequisites']}\n")
        
        explanation = "\n".join(parts)
    
    else:  # standard
        parts = [f"# {topic.replace('_', ' ').title()}\n"]
        parts.append(f"**Definition:** {concept['definition']}\n")
        
        if 'time_complexity' in concept:
            parts.append("**Complexity:**")
            if isinstance(concept['time_complexity'], dict):
                for op, complexity in list(concept['time_complexity'].items())[:3]:
                    parts.append(f"  - {op}: {complexity}")
            else:
                parts.append(f"  - {concept['time_complexity']}")
            parts.append("")
        
        if 'use_cases' in concept:
            parts.append("**When to use:**")
            for uc in concept['use_cases'][:2]:
                parts.append(f"  - {uc}")
            parts.append("")
        
        if 'example' in concept:
            parts.append(f"**Example:**\n```python{concept['example']}```")
        
        explanation = "\n".join(parts)
    
    return explanation
