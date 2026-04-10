class Solution:
    def encode(self, num: int) -> str:
        return bin(num)[2:]

if __name__ == "__main__":
    print(Solution().encode(num=10))
