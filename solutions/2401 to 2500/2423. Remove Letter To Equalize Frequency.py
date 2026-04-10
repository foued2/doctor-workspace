import collections


class Solution:
    UNIQUE_CHAR_THRESHOLD = 1

    @staticmethod
    def equalFrequency(word: str) -> bool:
        # Calculate frequency of each character in the word
        char_frequency = collections.Counter(word)
        # Calculate the frequency of frequencies
        frequency_distribution = collections.Counter(char_frequency.values())

        # Check if all characters have the same frequency
        if Solution.all_frequencies_uniform(frequency_distribution):
            # If true, ensure all frequencies are 1
            return all(freq == Solution.UNIQUE_CHAR_THRESHOLD for freq in char_frequency.values())

        # More than two different frequencies cannot be balanced by removing one character
        if len(frequency_distribution) > 2:
            return False

        # Find the minimum and maximum frequencies
        min_frequency, max_frequency = min(char_frequency.values()), max(char_frequency.values())

        # Check if removing a single character with frequency 1 makes the distribution uniform
        if Solution.is_removable_single_character(min_frequency, frequency_distribution):
            return True

        # Check if removing the last occurrence of the most frequent character makes the distribution uniform
        if Solution.is_removable_last_occurrence_of_most_frequent(max_frequency, min_frequency, frequency_distribution):
            return True

        return False

    @staticmethod
    def all_frequencies_uniform(frequency_distribution):
        return len(frequency_distribution) == Solution.UNIQUE_CHAR_THRESHOLD

    @staticmethod
    def is_removable_single_character(min_frequency, frequency_distribution):
        return min_frequency == Solution.UNIQUE_CHAR_THRESHOLD and frequency_distribution[min_frequency] == 1

    @staticmethod
    def is_removable_last_occurrence_of_most_frequent(max_frequency, min_frequency, frequency_distribution):
        return max_frequency - min_frequency == Solution.UNIQUE_CHAR_THRESHOLD and frequency_distribution[
            max_frequency] == 1


if __name__ == '__main__':
    # Example usage of the function
    print(Solution.equalFrequency('aazz'))
