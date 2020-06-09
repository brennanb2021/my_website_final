class Node:
    def __init__(self, withs, withouts, name):
        self.withs = withs
        self.withouts = withouts
        self.name = name
        self.connections = []  # should be filled with Nodes
        self.connectionsFromOthersToRemove = []
        self.edgeWeights = {} #for now this is a dictionary of input: other node. Output: edge weight. So, will have a copy
                              #of this edge weight in other node.
    def __str__(self):
        return (self.name, self.connections)

    def addNode(self, toAdd, weight): #UNTESTED DO NOT USE
        self.connections.append(toAdd)
        self.edgeWeights[toAdd.name] = weight
        toAdd.connections.append(self)
        toAdd.edgeWeights[self.name] = weight

    def deleteConnection (self, other):
        for i in range(len(self.connections)):
            if self.connections[i].name == other:
                self.connections[i].connections.remove(self)
                self.connections[i].edgeWeights.pop(self)
        self.connections.remove(other)
        self.edgeWeights.pop(other)
        print("connection supposedly removed:", self.connections[other])

    def setConnections(self, everyPerson, index): #everyPerson = list of people. index = the spot that this Node is in
                                                  #in everyPerson, so I can easily skip over it.
        for i in range(len(everyPerson)): #go through every other Node
            if i is not index: #why would I make a connection to itself haha
                if self.withouts.__contains__(everyPerson[i].name) or everyPerson[i].withouts.__contains__(self.name):
                    #other person in list of withouts or : do NOT make a connection
                    everyPerson[i].addToConnectionsFromOthersToRemove(self)  # this adds to OTHER NODE LIST, then later remove it.
                else: #if I shouldn't make a connection, add to the list of Nodes to not make a connection with in the other node
                    self.connections.append(everyPerson[i])  # if this node is ok with the other person, make a connection.

    def setConnectionsNoZeroes(self, everyPerson, index): #everyPerson = list of people. index = the spot that this Node is in
                                                  #in everyPerson, so I can easily skip over it.
        for i in range(len(everyPerson)): #go through every other Node
            if i is not index: #why would I make a connection to itself haha
                if self.withouts.__contains__(everyPerson[i].name) or everyPerson[i].withouts.__contains__(self.name):
                    #other person in list of withouts or : do NOT make a connection
                    everyPerson[i].addToConnectionsFromOthersToRemove(self)  # this adds to OTHER NODE LIST, then later remove it.
                else: #if I shouldn't make a connection, add to the list of Nodes to not make a connection with in the other node
                    if self.withs.__contains__(everyPerson[i]): #only add if in preference list
                        self.connections.append(everyPerson[i])  # if this node is ok with the other person, make a connection.

    def initializeEdgeWeights(self, everyPerson):
        for i in everyPerson:
            if i in self.connections:
                self.edgeWeights[i.name] = 0 #initialize weights to everyone not in self.withouts

    def removeDirectionalConnections(self):
        for i in range(len(self.connectionsFromOthersToRemove)):
            if self.connections.__contains__(self.connectionsFromOthersToRemove[i]):
                self.connections.remove(self.connectionsFromOthersToRemove[i])
        for i in range(len(self.connectionsFromOthersToRemove)):
            if self.edgeWeights.__contains__(self.connectionsFromOthersToRemove[i].name):
                del self.edgeWeights[self.connectionsFromOthersToRemove[i].name]

    def addToEdgeWeights(self, everyPerson):
        for i in range(len(self.withs)): #edit the edge weights based on prefs of this person
            if self.edgeWeights.__contains__(self.withs[i]):
                self.edgeWeights[self.withs[i]] += (3-i) #add to edge weights, first index = +3, second = +2, third = +1
            else:
                #if self.withs[i] != "None":
                    #print(self.edgeWeights, "does not contain", self.withs[i])
                self.edgeWeights[self.withs[i]] = (3-i) #have to set it because can't add to a non existing value (above)

            for j in range(len(everyPerson)): #looks like I have to go through all other people to change the person on the other
                if everyPerson[j].name == self.withs[i]: #end's edge weight
                    everyPerson[j].addToEdgeWeightFromOtherPerson(self.name, (3-i)) #calling on node on other end, add same number

    def addToEdgeWeightFromOtherPerson(self, otherNodeName, number): #have to add to both own edge weight and node on other side.
        if self.edgeWeights.__contains__(otherNodeName):
            self.edgeWeights[otherNodeName] += number
        else:
            self.edgeWeights[otherNodeName] = number #can't add to a dictionary key that doesn't exist yet, have to make it first.

    def getConnections(self):
        return self.connections

    def addToConnectionsFromOthersToRemove(self, remNode):
        self.connectionsFromOthersToRemove.append(remNode)

    def getEdgeWeights(self):
        return self.edgeWeights

    def clearConnections(self):
        self.connections = []
        self.edgeWeights = {}