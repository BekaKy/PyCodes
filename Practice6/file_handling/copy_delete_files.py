import shutil
import os
filePath = "D:/PyCodes/Practice6/file_handling/sample.txt"
shutil.copy(filePath, "D:/PyCodes/Practice6/file_handling/wheretocopy")

os.remove("D:/PyCodes/Practice6/file_handling/wheretocopy/sample.txt")
