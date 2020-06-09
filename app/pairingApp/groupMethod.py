from app.pairingApp.Node import Node
def findGroups(everyPerson):
    #Will use Prims if can implement.
    adj = [] #2d array
    for i in range(len(everyPerson)):
        row = []
        for j in range(len(everyPerson)):
            row.append(0)
            if everyPerson[i].getEdgeWeights().__contains__(everyPerson[j].name): #i has connection with j
                row[j] = everyPerson[i].getEdgeWeights()[everyPerson[j].name]
            else:
                row[j] = -1
        adj.append(row)

    alreadyGroupedNodes = []
    groupings = [] #array of arrays of size of 2 nodes
    cantmakeConnection = []

    while len(alreadyGroupedNodes) != (len(everyPerson)-len(cantmakeConnection)): #not all nodes have been grouped
        lgstEdge = -1
        lgstEdgeIndex = [-1,-1]
        for x in range(len(adj)):
            lgstEdgePerx = -1
            if x not in cantmakeConnection:
                for y in range(len(adj[x])):
                    if x not in alreadyGroupedNodes and y not in alreadyGroupedNodes:
                        if adj[x][y] > lgstEdge:
                            lgstEdge = adj[x][y] #find largest edge in all of the graph
                            lgstEdgeIndex = [x,y]
                        if adj[x][y] > lgstEdgePerx:
                            lgstEdgePerx = adj[x][y]
                if x not in alreadyGroupedNodes and x not in cantmakeConnection and lgstEdgePerx == -1: #at the end of going through x, add to cantmakeConnection if it has zero connections.
                    cantmakeConnection.append(x) #Has no connections left.
        if lgstEdge != -1:
            alreadyGroupedNodes.append(lgstEdgeIndex[0])
            alreadyGroupedNodes.append(lgstEdgeIndex[1])  # add both people to alreadygrouped
            group = [everyPerson[lgstEdgeIndex[0]], everyPerson[lgstEdgeIndex[1]]]
            groupings.append(group)

    groupingDict = {}
    groupsArr = []
    for i in range(len(groupings)):
        strBuild = groupings[i][0].name + " and " + groupings[i][1].name
        strBuild+=" ("+str(groupings[i][0].getEdgeWeights()[groupings[i][1].name])+")" #edge weight between them
        groupsArr.append(strBuild)
    groupingDict["groups"] = groupsArr

    cantBeGroupedArr = []
    for i in cantmakeConnection:
        cantBeGroupedArr.append(everyPerson[i].name)
    groupingDict["cantBeGrouped"] = cantBeGroupedArr
    

    #making the new graph, deleting nodes and resetting edge weights
    everyPersonNew = everyPerson
    emptyList = []
    for i in range(len(everyPersonNew)): #set cant make connections nodes equal to blank node.
        for j in cantmakeConnection:
            if everyPersonNew[i] == everyPerson[j]:
                everyPersonNew[i] = Node(emptyList, emptyList, everyPerson[j].name)

    for i in range(len(everyPersonNew)):
        for j in groupings:
            if everyPersonNew[i] == j[0]: #find the grouping nodes in everyPerson
                cxns = []
                cxns.append(j[1])
                everyPersonNew[i].connections = cxns
                edgeWeights = {}
                if everyPersonNew[i].name in j[1].getEdgeWeights():
                    edgeWeights[j[1].name] = j[1].getEdgeWeights()[everyPersonNew[i].name] #set edge weights
                    everyPersonNew[i].edgeWeights = edgeWeights
            elif everyPersonNew[i] == j[1]: #check the other one
                cxns = []
                cxns.append(j[0])
                everyPersonNew[i].connections = cxns
                edgeWeights = {}
                edgeWeights[j[0].name] = j[0].getEdgeWeights()[everyPersonNew[i].name]  # set edge weights
                everyPersonNew[i].edgeWeights = edgeWeights
    
    return [everyPersonNew, groupingDict]


  