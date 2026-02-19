# 1
n = int(input())
a = [x*x for x in range(n)]
print(a)
# 2
n = int(input())
b = [x for x in range(0, n) if x%2 == 0]
print(*b, sep=", ")
# 3
def Divisible(n):
    for i in range(0, n):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input())
b = Divisible(n)
print(next(b))
# 4
def squares(a, b):
    for i in range(a, b):
        yield i*i
a, b = map(int, input().split())
for s in squares(a, b):
    print(s)
# 5
n = int(input())
a = [x for x in range(n, 0, -1)]
print(*a, sep=", ")