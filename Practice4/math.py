import math as mh
# 1
deg = int(input())
print(mh.radians(deg))
# 2
h, b1, b2 = map(float, input().split())
print(((b1+b2)/2)*h)
# 3
def regular_polygon_area(n_sides, s_length):
    return (n_sides * s_length**2) / (4 * mh.tan(mh.pi / n_sides))

a, b = map(int, input().split())
print(regular_polygon_area(a, b))
# 4
b, h = map(float, input().split())
print(b*h)
