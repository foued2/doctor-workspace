class Solution:
    @staticmethod
    def defangIPaddr(address: str) -> str:

        # Using the replace() method to replace each '.' with '[.]'
        return address.replace(".", "[.]")


if __name__ == '__main__':
    print(Solution.defangIPaddr("255.100.50.0"))
