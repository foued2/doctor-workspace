from typing import List


class Solution:
    @staticmethod
    def topKFrequent(words: List[str], k: int) -> List[str]:
        # Use a dictionary to count the frequency of each word
        count = {}

        # Iterate through each word in the input list
        for word in words:
            # Increment the word count in the dictionary
            count[word] = count.get(word, 0) + 1

        # Sort the dictionary keys (words) first by frequency (descending), then by lexicographical order (ascending)
        sorted_words = sorted(count, key=lambda x: (-count[x], x))

        # Return the top k words from the sorted list
        return sorted_words[:k]


# Example usage to print the top k frequent words
if __name__ == "__main__":
    print(Solution().topKFrequent(words=["i", "love", "leetcode", "i", "love", "coding"], k=2))


from typing import List
import heapq


class Solution:
    @staticmethod
    def topKFrequent(words: List[str], k: int) -> List[str]:
        # Step 1: Count the frequency of each word using Counter from collections module
        freq_map = Counter(words)

        # Step 2: Build a heap of the top k frequent elements
        heap = [(-freq, word) for word, freq in freq_map.items()]

        # Step 3: Convert list to a heap in-place
        heapq.heapify(heap)

        # Step 4: Extract the top k elements from the heap, ensure they maintain the correct order
        top_k = [heapq.heappop(heap)[1] for _ in range(k)]

        return top_k


# Example usage to print the top k frequent words
if __name__ == "__main__":
    print(Solution().topKFrequent(words=["i", "love", "leetcode", "i", "love", "coding"], k=2))


from typing import List


class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.words = []


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, frequency: int):
        node = self.root
        for char in word:
            node = node.children[char]
        node.words.append((frequency, word))

    def topKWords(self, k: int) -> List[str]:
        result = []
        self._dfs(self.root, result, k)
        return result

    def _dfs(self, node: TrieNode, result: List[str], k: int):
        if not node:
            return
        # Sort the `node.words` first by frequency in descending order, then by lexicographical order
        node.words.sort(key=lambda x: (-x[0], x[1]))
        for frequency, word in node.words:
            if len(result) < k:
                result.append(word)
        for child in node.children.values():
            if len(result) >= k:
                break
            self._dfs(child, result, k)


class Solution:
    @staticmethod
    def topKFrequent(words: List[str], k: int) -> List[str]:
        freq_map = Counter(words)
        trie = Trie()
        for word, freq in freq_map.items():
            trie.insert(word, freq)
        return trie.topKWords(k)


# Example usage to print the top k frequent words
if __name__ == "__main__":
    print(Solution().topKFrequent(words=["i", "love", "leetcode", "i", "love", "coding"], k=2))


from typing import List
from collections import Counter, defaultdict


class Solution:
    @staticmethod
    def topKFrequent(words: List[str], k: int) -> List[str]:
        # Step 1: Count the frequency of each word using Counter from collections module
        freq_map = Counter(words)

        # Step 2: Create a bucket for each frequency
        max_freq = max(freq_map.values())
        buckets = [[] for _ in range(max_freq + 1)]

        # Step 3: Populate the buckets
        for word, freq in freq_map.items():
            buckets[freq].append(word)

        # Step 4: Sort words within each bucket lexicographically
        for bucket in buckets:
            bucket.sort()

        # Step 5: Collect the top k frequent words
        result = []
        for freq in range(max_freq, 0, -1):
            for word in buckets[freq]:
                result.append(word)
                if len(result) == k:
                    return result

        return result


# Example usage to print the top k frequent words
if __name__ == "__main__":
    print(Solution().topKFrequent(words=["i", "love", "leetcode", "i", "love", "coding"], k=2))