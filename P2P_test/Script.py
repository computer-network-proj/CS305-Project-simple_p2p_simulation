import os

#开启tracker
os.system('python SimpleTest.py > SimpleTest.txt')
print("SimpleTest.py ok")
os.system('python ComplexTest.py > ComplexTest.txt')
print("ComplexTest.py")
os.system('python mediumPeopleTest.py > mediumPeopleTest.txt')
print("mediumPeopleTest.py")
os.system('python ManyPeopleTest.py > ManyPeopleTest.txt')
os.system('python meduimFileTest.py > meduimFileTest.txt')
os.system('python largeFileTest.py > largeFileTest.txt')
os.system('python doomTest.py > doomTest.txt')
os.system('python simpleTitfortatTest.py > simpleTitfortatTest.txt')
os.system('python SpeedTest.py > SpeedTest.txt')