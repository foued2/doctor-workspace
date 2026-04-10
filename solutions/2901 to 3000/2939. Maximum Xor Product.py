class Solution:
    @staticmethod
    def maximumXorProduct(a: int, b: int, n: int) -> int:
        """
        Indeed, start by converting 'a' and 'b' to binary representation. This will be useful for seeing bitwise
        operations more clearly. After that, we need to loop over 'x' from 0 to '2^n-1'. For simplicity, you can use
        decimal counting, but keep in mind that the XOR operation works on binary representations. Note: In the case
        that a number 'x' has fewer bits in its binary representation than 'n', you would add leading zeroes to its
        binary representation until it has 'n' bits (however, we don't need to do it explicitly if we are using
        programming languages because they handle it by default). For each 'x', compute 'a XOR x' and 'b XOR x'.
        After calculating 'a XOR x' and 'b XOR x', multiply these two results together to get the product for that
        particular 'x'. Maintain a variable to store the maximum product found so far. If the product for an 'x' is
        greater than the stored maximum, update the maximum. Continue this process for each 'x'. In the end,
        the maximum variable will hold the maximum product of 'a XOR x' and 'b XOR x' for 'x' in the range [0,
        2^n). The answer could be a very large number, so the problem asks for the answer modulo 10^9 + 7 (to prevent
        integer overflow and keep the number manageable). So, return the maximum product modulo 10^9 + 7.
        :param a:
        :param b:
        :param n:
        :return:
        """

    #     bin_a = list(bin(a)[2:])
    #     bin_b = list(bin(b)[2:])
    #     max_res_a_x = 0
    #
    #     for x in range((2 ** n) - 1):
    #         res_a_x = list()
    #         bin_x = list(bin(x)[2:])
    #
    #         if len(bin_a) > len(bin_x):
    #             bin_x = ["0" for _ in range(len(bin_a) - len(bin_x))] + bin_x
    #         elif len(bin_a) < len(bin_x):
    #             bin_a = ["0" for _ in range(len(bin_x) - len(bin_a))] + bin_a
    #         for i in range(len(bin_a)):
    #
    #             if bin_a[i] != bin_x[i]:
    #                 res_a_x.append("1")
    #             else:
    #                 res_a_x.append("0")
    #         a_xor_x = int(''.join(map(str, res_a_x)), 2)
    #         if a_xor_x > max_res_a_x:
    #             max_res_a_x = a_xor_x
    #     print(max_res_a_x)


print(Solution.maximumXorProduct(570713374625622, 553376364476768, 35))


class Solution:
    @staticmethod
    def maximumXorProduct(a: int, b: int, n: int) -> int:
        def Xoring(x: int, n: int) -> int:
            bin_x = str((bin(x)[2:]))[::-1]
            i = 0
            while x < (2 ** n):
                x = (2 ** i) + x
                bin_x = '1' + bin_x
                print(bin_x)
                x = int(bin_x)
                print(x)
                i += 1
            return x
        print(Xoring(7, 4))
