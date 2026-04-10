class Solution:
    @staticmethod
    def toGoatLatin(sentence: str) -> str:
        # Initialize an empty list to store the transformed words
        res = []

        # Split the input sentence into individual words
        sentence = sentence.split()

        # Define a set of vowels for easy lookup
        vowels = set('aeiouAEIOU')

        # Iterate over each word and its index in the sentence
        for i, word in enumerate(sentence):
            # Check if the first letter of the word is a vowel
            if word[0] in vowels:
                # If it is a vowel, append 'ma' to the end of the word
                word += 'ma'
            else:
                # If it is not a vowel, move the first letter to the end and then append 'ma'
                word = word[1:] + word[0] + 'ma'

            # Add 'a' repeated (i + 1) times to the end of the word
            word += 'a' * (i + 1)

            # Append the transformed word to the result list
            res.append(word)

        # Join the list of transformed words into a single string with spaces in between
        res = ' '.join(res)

        # Return the final Goat Latin sentence
        return res


print(Solution.toGoatLatin(sentence="The quick brown fox jumped over the lazy dog"))
