with open("sample.txt", "a+") as file:
    writing = file.write(input())
file.seek(0)
text = file.read()
print(text)
file.close()