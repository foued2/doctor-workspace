class Solution:
    @staticmethod
    def countPrimes(n: int) -> int:
        if n <= 2:
            return 0
        primes_count = 0
        # Python program to print all primes smaller than or equal to n using Sieve of Eratosthenes

        # Create a boolean array "prime[0.n]" and initialize all entries it as true.
        # A value in prime[i] will finally be false if i is Not a prime, else true.
        prime = [True for _ in range(n + 1)]
        p = 2
        while p <= n:

            # If prime[p] is not changed, then it is a prime
            if prime[p]:
                # Update all multiples of p
                primes_count += 1  # Increment the counter for prime numbers

                for i in range(p * p, n + 1, p):
                    prime[i] = False
            p += 1

        return primes_count

    print(countPrimes(7))
