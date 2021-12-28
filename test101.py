import copy

"""
def generateList(listOri, idx, targetvule):

    contInsideI = copy.deepcopy(listOri[idx:len(listOri)])
    contI, cutFromOri = [], []
    for x in range(idx, len(listOri)):
        if listOri[x][2] == targetvule:
            contI.append(listOri[x])
            idx = x+1
    try:
        remainderA = copy.deepcopy(listOri[idx:len(listOri)])
        for item in remainderA:
            contInsideI.remove(item)
    except IndexError:
        pass

    cutFromOri = copy.deepcopy(contInsideI)

    for valA in contI:
        try:
            contInsideI.remove(valA)
        except ValueError:
            pass

    return cutFromOri, contI, contInsideI
"""

for i in range(1, 2):
    print(i)
