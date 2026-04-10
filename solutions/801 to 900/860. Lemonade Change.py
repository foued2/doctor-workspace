from typing import List


class Solution:
    @staticmethod
    def lemonadeChange(bills: List[int]) -> bool:
        # Initialize counters for $5 and $10 bills
        five_count = 0
        ten_count = 0

        # Iterate through each bill in the list
        for bill in bills:
            if bill == 5:
                # Increment $5 bill counter
                five_count += 1
            elif bill == 10:
                if five_count == 0:
                    # Cannot give change for $10 bill
                    return False
                # Give $5 change and increment $10 bill counter
                five_count -= 1
                ten_count += 1
            else:  # bill == 20
                if ten_count > 0 and five_count > 0:
                    # Give one $10 bill and one $5 bill as change
                    ten_count -= 1
                    five_count -= 1
                elif five_count >= 3:
                    # Give three $5 bills as change
                    five_count -= 3
                else:
                    # Cannot give change for $20 bill
                    return False

        # All transactions successful
        return True


print(Solution.lemonadeChange(bills=[5, 5, 10, 20, 5, 5, 5, 5, 5, 5, 5, 5, 5, 10, 5, 5, 20, 5, 20, 5]))
