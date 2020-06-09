from app.pairingApp.Node import Node
from app.pairingApp.excelImporter import get_names
#from package.Prims import Prims
import numpy as np

import networkx as nx
import matplotlib.pyplot as plt
from app.pairingApp.groupMethod import findGroups
import base64
from io import BytesIO
    
def setAll(everyPerson): #sets the Node connections and removes connections that people don't want.
    for i in range(len(everyPerson)):
        everyPerson[i].setConnections(everyPerson, i)
    for i in range(len(everyPerson)):
        everyPerson[i].initializeEdgeWeights(everyPerson)
    for i in range(len(everyPerson)):
        everyPerson[i].addToEdgeWeights(everyPerson)
    for i in range(len(everyPerson)):
        everyPerson[i].removeDirectionalConnections()

def getGroups(everyPerson):
    return findGroups(everyPerson)
    #return prims(everyPerson)

def createGraph(everyPerson):
    graph = nx.Graph()
    for i in range(len(everyPerson)):  # add all people as nodes to graph
        graph.add_node(everyPerson[i].name)

    for i in range(len(everyPerson)):  # go through all i nodes
        for j in range(len(everyPerson)):  # for each i node, go through all j other nodes to check for connections
            if everyPerson[i].getEdgeWeights().__contains__(
                    everyPerson[j].name):  # if the dictionary of edges has an edge bw everyperson[i] and [j]
                graph.add_edge(everyPerson[i].name, everyPerson[j].name,
                               weight=everyPerson[i].getEdgeWeights()[everyPerson[j].name])

    return graph

def plotGraph(graph, distEdges, name):
    pos = nx.spring_layout(graph, k=distEdges)  # positions for all nodes

    nx.draw_networkx_nodes(graph, pos, node_size=700) # nodes
    nx.draw_networkx_edges(graph, pos, edgelist=graph.edges, width=2) # edges
    nx.draw_networkx_labels(graph, pos, font_color="red", font_size=7, font_family='sans-serif')
    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_color=(0, 0.5, 0.2), font_size=10, font_family='sans-serif')

    plt.suptitle(name)
    plt.axis('off')

    tmpfile = BytesIO()
    plt.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    html = '<img src=\'data:image/png;base64,{}\'>'.format(encoded)
    plt.clf()
    return html


def runPairer(file):
    
    tempList = get_names(file)
    everyPerson = []
    onlyConnections = []
    onlyConnectionsCopy = []

    for i in tempList:
        everyPerson.append(Node(i[1], i[2], i[0]))
        if i[1][0] != "None" or i[1][1] != "None" or i[1][2] != "None":
            onlyConnections.append(Node(i[1], i[2], i[0]))
            onlyConnectionsCopy.append(Node(i[1], i[2], i[0]))

    for i in range(len(everyPerson)): #There is a "None None" person in everyperson, remove it.
        if everyPerson[i].name == "None None":
            everyPerson.remove(everyPerson[i])

    setAll(everyPerson)
    setAll(onlyConnections)

    #set onlyConnectionsCopy without setAll, need to use setConnectionsNoZeroes to only show relevant nodes.
    for i in range(len(onlyConnectionsCopy)):
        onlyConnectionsCopy[i].setConnectionsNoZeroes(onlyConnectionsCopy, i)
    for i in range(len(onlyConnectionsCopy)):
        onlyConnectionsCopy[i].addToEdgeWeights(onlyConnectionsCopy)
    for i in range(len(onlyConnectionsCopy)):
        onlyConnectionsCopy[i].removeDirectionalConnections()


    #Open the pair.html in templates and append the images of the plots to it (get the text, edit the text, and return the text.)
    with open('./app/pairingApp/pairhtmlcopyDynamic.html','r') as f:
        addThisHtml = f.read()
    

    gotGroupsTest = getGroups(everyPerson)
    groupedPeopleTEST = gotGroupsTest[0]
    everybodyConnections = gotGroupsTest[1]
    graph2Cxns = createGraph(groupedPeopleTEST)
    html = plotGraph(graph2Cxns, None, "Connections found in graph of everyone")
    addThisHtml = addThisHtml.replace('Input graph -Connections found in graph of only people with preferences- here', html)

    everyPersonNames = []
    for i in everyPerson:
        everyPersonNames.append(i.name)
    onlyConnectionsNames = []
    for i in onlyConnections:
        onlyConnectionsNames.append(i.name)

    noPrefList = []
    for i in everyPersonNames:
        if i not in onlyConnectionsNames:
            noPrefList.append(i)


    gotGroups = getGroups(onlyConnections)
    groupedPeople = gotGroups[0]
    onlyHaveConnectionsConnections = gotGroups[1]
    graph2 = createGraph(groupedPeople)
    html = plotGraph(graph2, 3*1/np.sqrt(len(graph2.nodes())), "Connections found in graph of only people with preferences")
    addThisHtml = addThisHtml.replace('Input graph -Connections found in graph of everybody- here', html)

    graphOnlyCxnsNoZeroes = createGraph(onlyConnectionsCopy)
    html = plotGraph(graphOnlyCxnsNoZeroes, 3 * 1 / np.sqrt(len(graphOnlyCxnsNoZeroes.nodes())),
              "Complete graph of only people with preferences")
    addThisHtml = addThisHtml.replace('Input graph -Complete graph of only people with preferences- here', html)

    #added the nondynamic part before, now add the dynamic part.
    with open('./app/templates/pair.html','a') as f:
        f.write(addThisHtml)

    return [everybodyConnections, onlyHaveConnectionsConnections]
    
