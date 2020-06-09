import sys
from collections import defaultdict
def Prims(everyPerson):
    adj = []  # 2d array
    # selectedCol = 0 #where to start with the adjacency matrix stuff
    # largestEdgeNum = 0
    for i in range(len(everyPerson)):
        row = []
        for j in range(len(everyPerson)):
            row.append(0)
            if everyPerson[i].getEdgeWeights().__contains__(everyPerson[j].name):  # i has connection with j
                row[j] = everyPerson[i].getEdgeWeights()[everyPerson[j].name]
                # if everyPerson[i].getEdgeWeights()[everyPerson[j].name] > largestEdgeNum:
                # largestEdgeNum = everyPerson[i].getEdgeWeights()[everyPerson[j].name]
                # selectedCol = i
            else:
                row[j] = -1
            if j != len(everyPerson) - 1:
                print(row[j], end=" ")
            else:
                print(row[j])

        adj.append(row)

