class Solution:
    @staticmethod
    def strongPasswordCheckerII(password: str) -> bool:
        # List of special characters
        special_characters = "!@#$%^&*()-+"

        # Boolean flags to check the required conditions
        has_eight_characters = len(password) >= 8
        has_one_lowercase = False
        has_one_uppercase = False
        has_one_digit = False
        has_one_special_character = False
        has_no_consecutive_characters = True

        # Check each character in the password
        for i in range(len(password)):
            char = password[i]
            if char.islower():
                has_one_lowercase = True
            elif char.isupper():
                has_one_uppercase = True
            elif char.isdigit():
                has_one_digit = True
            elif char in special_characters:
                has_one_special_character = True
            # Check for consecutive characters
            if i > 0 and char == password[i - 1]:
                has_no_consecutive_characters = False

        # Return True if all conditions are satisfied
        return (has_eight_characters and has_one_lowercase and has_one_uppercase and
                has_one_digit and has_one_special_character and has_no_consecutive_characters)


print(Solution.strongPasswordCheckerII(password="IloveLe3decode!"))
