s = ""
t = "LOWLODAODTWHOEXSELR"
i = 10
while len(s) < 10:
    i += 1
    j = 2
    k = True
    while j < i and k:
        k = i % j
        j += 1
    if k:
        s += t[j % len(t)]
print(s)