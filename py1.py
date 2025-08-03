s = ""
t = "LOWLODAODTWHOEXSELR"
i = 11

def is_prime(n):
    return all(n % j for j in range(2, int(n**0.5) + 1))

while len(s) < 10:
    if is_prime(i):
        s += t[i % len(t)]
    i += 1

print(s)
