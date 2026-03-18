import os

os.makedirs("newfolder/evennewerfolder", exist_ok=True)
allDirs = os.listdir("D:/PyCodes/Practice6/directory_management")
print(allDirs)
extension = ".py"
files = [file for file in allDirs if file.endswith(extension)]
print(files)