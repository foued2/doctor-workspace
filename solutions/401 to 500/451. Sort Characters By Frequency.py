import collections
import heapq


class Solution:
    @staticmethod
    def frequencySort(s: str) -> str:
        # Step 1: Count the frequency of each character in the string using Counter
        counter = collections.Counter(s)

        # Counter is a subclass of dictionary where elements are stored as dictionary keys
        # and their counts are stored as dictionary values.
        # Example: if s = "tree", counter = {'t': 1, 'r': 1, 'e': 2}

        # Step 2: Sort the items of the counter by frequency in descending order
        # sorted() function returns a list of tuples, where each tuple is (character, frequency)
        counter = sorted(counter.items(), key=lambda x: x[1], reverse=True)

        # Sorting converts the Counter dictionary items into a list of tuples because
        # sorted() operates on iterables and returns a list.
        # Example: if counter = Counter({'e': 2, 't': 1, 'r': 1}),
        # After sorting: counter = [('e', 2), ('t', 1), ('r', 1)]

        ans = ""

        # Step 3: Construct the resultant string by repeating each character
        # according to its frequency
        for i in counter:
            ans += i[0] * i[1]
            # i[0] is the character
            # i[1] is its frequency
            # Example: for ('e', 2), it will add 'ee' to the result string

        return ans


if __name__ == '__main__':
    # Test the solution with an example
    print(Solution().frequencySort("tree"))  # Output: "eert" or "eetr"


class Solution:
    @staticmethod
    def frequencySort(s: str) -> str:
        """
        Bucket Sort
        """
        # Step 1: Count the frequency of each character using Counter
        counter = collections.Counter(s)

        # Step 2: Create buckets where index represents frequency and value holds a list of characters
        max_freq = max(counter.values())
        buckets = [[] for _ in range(max_freq + 1)]

        # Populate the buckets
        for char, freq in counter.items():
            buckets[freq].append(char)

        # Step 3: Build the result string by concatenating characters from the buckets
        ans = []
        for freq in range(max_freq, 0, -1):
            for char in buckets[freq]:
                ans.append(char * freq)

        return ''.join(ans)


if __name__ == '__main__':
    # Test the solution with an example
    print(Solution().frequencySort("tree"))  # Output: "eert" or "eetr"


class Solution:
    @staticmethod
    def frequencySort(s: str) -> str:
        """
        Heap Sort
        """
        # Step 1: Count the frequency of each character using Counter
        counter = collections.Counter(s)

        # Step 2: Create a max-heap based on the frequency of characters
        max_heap = [(-freq, char) for char, freq in counter.items()]
        heapq.heapify(max_heap)

        # Step 3: Build the result string by extracting from heap
        ans = []
        while max_heap:
            freq, char = heapq.heappop(max_heap)
            ans.append(char * -freq)  # multiply char by its frequency

        return ''.join(ans)


if __name__ == '__main__':
    # Test the solution with an example
    print(Solution().frequencySort("tree"))  # Output: "eert" or "eetr"
