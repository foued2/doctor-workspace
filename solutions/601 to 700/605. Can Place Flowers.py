from typing import List


class Solution:
    @staticmethod
    def canPlaceFlowers(flowerbed: List[int], n: int) -> bool:
        counter = 0

        # Ensure that the first position and the position after the last flower are available
        flowerbed = [0] + flowerbed + [0]

        for i in range(1, len(flowerbed) - 1):
            if flowerbed[i - 1] == flowerbed[i] == flowerbed[i + 1] == 0:
                flowerbed[i] = 1
                counter += 1

        return counter >= n


# Test the function
print(Solution.canPlaceFlowers(flowerbed=[1, 0, 0, 0, 0, 1], n=1))  # Output: True
print(Solution.canPlaceFlowers(flowerbed=[1, 0, 0, 0, 0, 0, 1], n=2))  # Output: False


# from typing import List
#
#
# class Solution:
#     @staticmethod
#     def canPlaceFlowers(flowerbed: List[int], n: int) -> bool:
#         """
#         :param flowerbed:
#         :param n:
#         :return:
#         """
#         if flowerbed == [0] and n == 1: return True
#         counter = 0
#         if flowerbed[:2] == [0, 0]:
#             flowerbed[0] = 1
#             counter += 1
#         if flowerbed[-2:] == [0, 0] and len(flowerbed) > 2:
#             flowerbed[-1] = 1
#             counter += 1
#
#         for i in range(0, len(flowerbed)):
#             if flowerbed[i: i + 3] == [0, 0, 0]:
#                 flowerbed[i + 1] = 1
#                 counter += 1
#         # print(counter)
#         return counter >= n
#
#     print(canPlaceFlowers(flowerbed=[1, 0, 0, 0], n=4))
