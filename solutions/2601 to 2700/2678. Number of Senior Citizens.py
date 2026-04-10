from typing import List


class Solution:
    @staticmethod
    def countSeniors(details: List[str]) -> int:
        res = 0
        for detail in details:
            # Extract the age using slicing based on the fixed index and length
            age = int(detail[11:13])
            if age > 60:  # Check if the age is greater than 60
                res += 1  # Increment the count of seniors
        return res


print(Solution.countSeniors(details=["1313579440F2036", "2921522980M5644"]))
