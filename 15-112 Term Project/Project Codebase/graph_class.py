# Defining methods for a graph class with inspiration from 
# Source: Kian's code from Graph TA-led mini lecture 
# https://scs.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=dfed1c3d
# -259d-4c50-8d84-ae65013a6ffb

class Graph():
    def __init__(self):
        self.graph = {}
         
     #Adds a node to the graph
    def addNode(self, node):
        self.graph[node] = {}

    def addSetasVal(self, parentNode, setToBeAdded):
        for node in setToBeAdded:
            self.graph[parentNode].add(node)

    # Adds an edge connecting two different nodes - specifically tailored to use for Kruskal
    def addEdgeWeightless(self, nodeA, nodeB):
        if nodeA not in self.graph:
            self.graph[nodeA] = {nodeB}
        else:
            self.graph[nodeA].add(nodeB)

    # Adds an edge connecting two different nodes with weight
    def addEdge(self, nodeA, nodeB, weight = 1):
        if nodeA not in self.graph:
            self.graph[nodeA] = {}
        if nodeB not in self.graph:
            self.graph[nodeB] = {}
        self.graph[nodeA][nodeB] = weight
        self.graph[nodeB][nodeA] = weight
    
    # Returns the node that maps to the edge
    def getParentNode(self, edge):
        for node in self.graph:
            if edge in self.graph[node]:
                return node
        return {}
    
    # Returns all the nodes in the graph
    def getNodes(self):
        return list(self.graph)

    # Returns the default edge weight of two connected nodes
    def getEdgeWeight(self, nodeA, nodeB):
        return self.graph[nodeA][nodeB]
        
    # Returns a list of the neighbors of a particular node 
    def getConnectedNodesUnweighted(self, parentNode):
        neighbors = []
        for node in self.graph[parentNode]:
            neighbors.append(node)
        return neighbors

    def getConnectedNodesWeighted(self, parentNode):
        neighbors = []
        for edge in self.graph[parentNode]:
            neighbors.append(edge)
        return neighbors

    def orderedGraph(self):
        return dict(sorted(self.graph.items()))

    def printGraph(self):
        nodeLst = sorted(list(self.graph)) # Sorts the list of nodes in order 
        print("               ")
        print("Printing graph... ")
        for node in nodeLst:
            print("    ", node, " : ", (self.graph[node]))
        