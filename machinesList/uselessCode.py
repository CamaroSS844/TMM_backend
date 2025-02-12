thelist = ["taboka", "david", "taboka", "samuel", "tanaka", "tanaka", "durrell"]
finalList = []
def single(i):
    global finalList
    if i not in finalList:
            finalList.append(i)

list(map(single, thelist))

print(finalList)
