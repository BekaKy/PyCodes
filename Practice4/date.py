import datetime
# 1
day = datetime.datetime.now()
print(int(day.strftime("%d"))-5)
# 2
day = datetime.datetime.now()
print(int(day.strftime("%d"))-1)
print(int(day.strftime("%d")))
print(int(day.strftime("%d"))+1)
# 3
day = datetime.datetime.now()
print(day.strftime("%f"))
# 4
y1, m1, d1 = map(int, input().split())
y2, m2, d2 = map(int, input().split())
day1 = datetime.datetime(y1, m1, d1)
day2 = datetime.datetime(y2, m2, d2)
insecs1 = int(day1.strftime("%Y"))*365*24*60*60+int(day1.strftime("%H"))*60*60+int(day1.strftime("%M"))*60+int(day1.strftime("%S"))
insecs2 = int(day2.strftime("%Y"))*365*24*60*60+int(day2.strftime("%H"))*60*60+int(day2.strftime("%M"))*60+int(day2.strftime("%S"))
print(insecs1-insecs2)