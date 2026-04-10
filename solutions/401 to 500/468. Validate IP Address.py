class Solution:
    @staticmethod
    def validIPAddress(queryIP: str) -> str:
        # Check if the IP is possibly IPv4 by counting dots
        if queryIP.count(".") == 3:
            validIPv4 = True
            # Split the IP address by dots and check each segment
            for i in queryIP.split("."):
                # Check for leading zeros in segments with multiple characters
                if len(i) > 1 and i[0] == "0":
                    validIPv4 = False
                    break
                # Check if the segment is a digit and in the valid range for IPv4
                if not i.isdigit() or not (0 <= int(i) <= 255):
                    validIPv4 = False
                    break
            # If all segments are valid
            if validIPv4:
                return "IPv4"

        # Set of valid hexadecimal characters for IPv6
        hex_chars = "0123456789abcdefABCDEF"

        # Check if the IP is possibly IPv6 by counting colons
        if queryIP.count(":") == 7:
            validIPv6 = True
            # Split the IP address by colons and check each segment
            for i in queryIP.split(":"):
                # Check if segments are empty or too long
                if len(i) == 0 or len(i) > 4:
                    validIPv6 = False
                # Check if each character in the segment is a valid hexadecimal character
                for j in i:
                    if j not in hex_chars:
                        validIPv6 = False
                        break
            # If all segments are valid
            if validIPv6:
                return "IPv6"

        # If neither IPv4 nor IPv6
        return "Neither"


# Test the function with a sample IPv4 address
if __name__ == "__main__":
    print(Solution().validIPAddress("172.16.254.1"))