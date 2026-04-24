"""
Phase 2 Perturbation Pack - One perturbation per base case, tagged by type.

Taxonomy:
  - lexical: word-level substitution, same meaning
  - objective: core goal reframed
  - constraint: ambiguity added/removed
  - disguise: domain shift, same structure, different problem type
"""

PERTURBATION_PACK = [
    # PARAPHRASE cases -> LEXICAL (word substitution)
    ("PARAPHRASE_TWO_SUM_ALPHA_LEXICAL", "two_sum",
     "Provided an array along with a target value, output indices of the two entries whose sum equals the target. Exactly one valid combination exists."),
    ("PARAPHRASE_TWO_SUM_BETA_LEXICAL", "two_sum",
     "Inputs: a collection of integers together with a goal sum. Outputs: index positions of two elements that together reach the goal. No alternative pairs are possible."),
    ("PARAPHRASE_LONGEST_PREFIX_LEXICAL", "longest_common_prefix",
     "Receiving several text strings, determine the longest common prefix that begins every string. Return empty string when no match."),
    ("PARAPHRASE_VALID_PARENS_LEXICAL", "valid_parentheses",
     "Check that every opening bracket has a matching closing bracket in proper nesting order. Respond true or false."),
    ("PARAPHRASE_MERGE_LISTS_LEXICAL", "merge_two_sorted_lists",
     "Combine two already-sorted sequences into one sorted sequence. Maintain the ordering."),

    # SIMILAR cases -> OBJECTIVE SWAP (reframe the goal)
    ("SIMILAR_MAX_SUM_VS_PRODUCT_OBJ", "max_subarray",
     "Find the contiguous subarray with the maximum product. (vs maximum SUM would be different)"),
    ("SIMILAR_TWO_SUM_VS_THREE_SUM_OBJ", "three_sum",
     "Find three numbers in the array that add up to zero. (vs Two Sum - different count)"),
    ("SIMILAR_CLIMBING_WAYS_VS_COST_OBJ", "climbing_stairs",
     "Find the minimum cost to reach the top. (vs number of ways would be different)"),
    ("SIMILAR_LIS_VS_LCS_OBJ", "longest_increasing_subsequence",
     "Find the longest common subsequence between two arrays. (vs longest increasing - similar structure, different problem)"),
    ("SIMILAR_DFS_VS_BFS_TRAVERSAL_OBJ", None,
     "Visit all nodes in the structure below using breadth-first order:\n    1\n   / \\\n  2   3"),

    # AMBIG cases -> CONSTRAINT (add/remove ambiguity)
    ("AMBIG_SHORTEST_PATH_CONSTRAINT", None,
     "Find the shortest path from start to end. You may move in any cardinal direction on an infinite grid."),
    ("AMBIG_MAX_ELEMENT_CONSTRAINT", None,
     "Find the maximum element in the array."),
    ("AMBIG_FIND_PAIRS_CONSTRAINT", None,
     "Find all pairs of elements that satisfy the condition (elements must sum to an even number)."),
    ("AMBIG_SORTED_OUTPUT_CONSTRAINT", None,
     "Return a sorted version of the input using merge sort."),
    ("AMBIG_TRAVERSE_CONSTRAINT", None,
     "Traverse the binary tree below in depth-first order:\n    1\n   / \\\n  2   3"),

    # DOMAIN DISGUISE (non-algorithmic surface similarity)
    ("DISGUISE_TWO_SUM_SHOPPING", "two_sum",
     "Given a shopping list with item prices and a budget, identify which two items can be purchased together without exceeding the budget."),
    ("DISGUISE_LIS_TIMESERIES", "longest_increasing_subsequence",
     "Given daily stock prices over a month, find the longest consecutive period where prices were consistently rising."),
    ("DISGUISE_MAX_SUM_BUDGET", "max_subarray",
     "Given daily expenses over a week, find the consecutive days with the highest total spending."),
    ("DISGUISE_VALID_PARENS_BRACKETS", "valid_parentheses",
     "Verify that all opening brackets [ and { have matching closing brackets ] and } in the correct sequence in an expression."),
]

# Expected outcomes
EXPECTED = {
    "PARAPHRASE_TWO_SUM_ALPHA_LEXICAL": ("two_sum", "match"),
    "PARAPHRASE_TWO_SUM_BETA_LEXICAL": ("two_sum", "match"),
    "PARAPHRASE_LONGEST_PREFIX_LEXICAL": ("longest_common_prefix", "match"),
    "PARAPHRASE_VALID_PARENS_LEXICAL": ("valid_parentheses", "match"),
    "PARAPHRASE_MERGE_LISTS_LEXICAL": ("merge_two_sorted_lists", "match"),
    "SIMILAR_MAX_SUM_VS_PRODUCT_OBJ": ("max_subarray", "match"),
    "SIMILAR_TWO_SUM_VS_THREE_SUM_OBJ": ("three_sum", "match"),
    "SIMILAR_CLIMBING_WAYS_VS_COST_OBJ": ("climbing_stairs", "match_or_reject"),
    "SIMILAR_LIS_VS_LCS_OBJ": ("longest_increasing_subsequence", "match"),
    "SIMILAR_DFS_VS_BFS_TRAVERSAL_OBJ": (None, "reject"),
    "AMBIG_SHORTEST_PATH_CONSTRAINT": (None, "reject"),
    "AMBIG_MAX_ELEMENT_CONSTRAINT": (None, "reject"),
    "AMBIG_FIND_PAIRS_CONSTRAINT": (None, "reject"),
    "AMBIG_SORTED_OUTPUT_CONSTRAINT": (None, "reject"),
    "AMBIG_TRAVERSE_CONSTRAINT": (None, "reject"),
    "DISGUISE_TWO_SUM_SHOPPING": ("two_sum", "match"),
    "DISGUISE_LIS_TIMESERIES": ("longest_increasing_subsequence", "match"),
    "DISGUISE_MAX_SUM_BUDGET": ("max_subarray", "match"),
    "DISGUISE_VALID_PARENS_BRACKETS": ("valid_parentheses", "match"),
}

PERTURBATION_TYPES = {
    "PARAPHRASE_TWO_SUM_ALPHA_LEXICAL": "lexical",
    "PARAPHRASE_TWO_SUM_BETA_LEXICAL": "lexical",
    "PARAPHRASE_LONGEST_PREFIX_LEXICAL": "lexical",
    "PARAPHRASE_VALID_PARENS_LEXICAL": "lexical",
    "PARAPHRASE_MERGE_LISTS_LEXICAL": "lexical",
    "SIMILAR_MAX_SUM_VS_PRODUCT_OBJ": "objective_swap",
    "SIMILAR_TWO_SUM_VS_THREE_SUM_OBJ": "objective_swap",
    "SIMILAR_CLIMBING_WAYS_VS_COST_OBJ": "objective_swap",
    "SIMILAR_LIS_VS_LCS_OBJ": "objective_swap",
    "SIMILAR_DFS_VS_BFS_TRAVERSAL_OBJ": "objective_swap",
    "AMBIG_SHORTEST_PATH_CONSTRAINT": "constraint_ambiguity",
    "AMBIG_MAX_ELEMENT_CONSTRAINT": "constraint_ambiguity",
    "AMBIG_FIND_PAIRS_CONSTRAINT": "constraint_ambiguity",
    "AMBIG_SORTED_OUTPUT_CONSTRAINT": "constraint_ambiguity",
    "AMBIG_TRAVERSE_CONSTRAINT": "constraint_ambiguity",
    "DISGUISE_TWO_SUM_SHOPPING": "domain_disguise",
    "DISGUISE_LIS_TIMESERIES": "domain_disguise",
    "DISGUISE_MAX_SUM_BUDGET": "domain_disguise",
    "DISGUISE_VALID_PARENS_BRACKETS": "domain_disguise",
}