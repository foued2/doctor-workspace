from typing import List


class Solution:
    @staticmethod
    def countCharacters(words: List[str], chars: str) -> int:
        """
        Hash table, Flag (True / False)
        """
        # Initialize the variable to store the total length of all good strings
        ans = 0

        # Create a dictionary to count the occurrences of each character in 'chars'
        table = {}
        for char in chars:
            table[char] = table.get(char, 0) + 1

        # Iterate over each word in the list of words
        for word in words:
            # Make a copy of the character table to use for checking the current word
            check = table.copy()
            # Assume the word can be formed
            can_form = True

            # Check each character in the current word
            for char in word:
                # If the character is in 'chars' and there is enough count
                if char in check and check[char] > 0:
                    check[char] -= 1
                else:
                    # If the character is not available or not enough, mark as cannot form the word
                    can_form = False
                    break

            # If the word can be formed, add its length to the total length
            if can_form:
                ans += len(word)

        # Return the total length of all good strings
        return ans


print(Solution.countCharacters(
    words=["dyiclysmffuhibgfvapygkorkqllqlvokosagyelotobicwcmebnpznjbirzrzsrtzjxhsfpiwyfhzyonmuabtlwin",
           "ndqeyhhcquplmznwslewjzuyfgklssvkqxmqjpwhrshycmvrb", "ulrrbpspyudncdlbkxkrqpivfftrggemkpyjl", "boygirdlggnh",
           "xmqohbyqwagkjzpyawsydmdaattthmuvjbzwpyopyafphx",
           "nulvimegcsiwvhwuiyednoxpugfeimnnyeoczuzxgxbqjvegcxeqnjbwnbvowastqhojepisusvsidhqmszbrnynkyop",
           "hiefuovybkpgzygprmndrkyspoiyapdwkxebgsmodhzpx",
           "juldqdzeskpffaoqcyyxiqqowsalqumddcufhouhrskozhlmobiwzxnhdkidr", "lnnvsdcrvzfmrvurucrzlfyigcycffpiuoo",
           "oxgaskztzroxuntiwlfyufddl", "tfspedteabxatkaypitjfkhkkigdwdkctqbczcugripkgcyfezpuklfqfcsccboarbfbjfrkxp",
           "qnagrpfzlyrouolqquytwnwnsqnmuzphne", "eeilfdaookieawrrbvtnqfzcricvhpiv",
           "sisvsjzyrbdsjcwwygdnxcjhzhsxhpceqz", "yhouqhjevqxtecomahbwoptzlkyvjexhzcbccusbjjdgcfzlkoqwiwue",
           "hwxxighzvceaplsycajkhynkhzkwkouszwaiuzqcleyflqrxgjsvlegvupzqijbornbfwpefhxekgpuvgiyeudhncv",
           "cpwcjwgbcquirnsazumgjjcltitmeyfaudbnbqhflvecjsupjmgwfbjo", "teyygdmmyadppuopvqdodaczob",
           "qaeowuwqsqffvibrtxnjnzvzuuonrkwpysyxvkijemmpdmtnqxwekbpfzs",
           "qqxpxpmemkldghbmbyxpkwgkaykaerhmwwjonrhcsubchs"],
    chars="usdruypficfbpfbivlrhutcgvyjenlxzeovdyjtgvvfdjzcmikjraspdfp"))
