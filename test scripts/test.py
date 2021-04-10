coolList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(coolList)
for item in coolList:
    if item <= 5:
        coolList.remove(item+1)

print(coolList)
print(coolList)