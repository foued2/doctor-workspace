# Create a class named Solution
class Solution:
    # define function fourSum as a static method, to find four numbers in a given list which sum is equal to target
    @staticmethod
    def fourSum(nums, target):
        # define a helping function named findNsum, given a sorted array, this function finds the number of tuple
        # whose sum is equal to the target.
        def findNsum(l, r, target, N, result, results):
            # if the number of elements in an array is less than N
            # OR N is less than 2
            # OR target is less than N times the smallest element in array
            # OR target is greater than N times the largest element in an array
            # then return from function, because we cannot find any tuple satisfying above conditions.
            if r - l + 1 < N or N < 2 or target < nums[l] * N or target > nums[r] * N:
                return
            # If N is equal to 2, then we want to find pairs whose sum is equal to the target.
            if N == 2:
                # Until l < r, iterate
                while l < r:
                    # calculate the sum of lth and rth element
                    s = nums[l] + nums[r]
                    # if a sum is equal to target, append the result to the results and increment l
                    if s == target:
                        results.append(result + [nums[l], nums[r]])
                        l += 1
                        # increment l to skip all the elements which are equal to its previous element to avoid
                        # considering a duplicate pair
                        while l < r and nums[l] == nums[l - 1]:
                            l += 1
                    # if a sum is less than target, increment l
                    elif s < target:
                        l += 1
                    # if a sum is greater than target, decrement r
                    else:
                        r -= 1
            # for every i from l to r iterate over the numbers and recursively find (N-1) numbers whose sum is
            # (target - nums[i])
            else:
                for i in range(l, r + 1):
                    # Increasing the pointer when digits are identical to avoid duplicate results
                    if i == l or (i > l and nums[i - 1] != nums[i]):
                        findNsum(i + 1, r, target - nums[i], N - 1, result + [nums[i]], results)

        # First sort the nums array, then send this sorted array to helper function which finds 4 numbers in this
        # array whose sum is equal to target.
        nums.sort()
        results = []
        findNsum(0, len(nums) - 1, target, 4, [], results)
        return results

    # Run the Four Sum Function
    print(fourSum([1, 0, -1, 0, -2, 2], 0))
