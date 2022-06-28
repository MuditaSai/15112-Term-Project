from node_class import *
from graph_class import * 

import random
class Kruskal():
    def __init__(self, rows, cols, gridGraph, connectedGraph):
        self.rows = rows
        self.cols = cols
        self.gridGraph = gridGraph
        self.connectedGraph = connectedGraph
        self.passages = []
        self.alreadyConnectedEdges = []

    @staticmethod
    # Returns a list of randomly shuffled node-neighbor tuples
    def generateRandomPassages(self):
        result = []
        repeats = set()
        for node in self.gridGraph:
            t = tuple()
            for neighbor in self.gridGraph[node]:
                t = (node, neighbor)
                # Prevents tuples such as (1,0) and (0,1) both being added
                if t not in repeats:
                    result.append(t)
                repeats.add((neighbor, node))
        # Destructively shuffles the list of tuples
        random.shuffle(result)
        print("result", result)
        self.passages = result
        print("passages", self.passages)

        elems = self.rows*self.cols 
        parent = [-1]*elems
        for (nodeA, nodeB) in self.passages:
            print("nodeA", nodeA)
            print("nodeB", nodeB)
            count = 0
            # potential because value could just be a child
            potentialParentA = nodeA
            potentialParentB = nodeB
            # if "parent" is +ve then it is not actually the parent...
            # so repeat process till we found the parent (i.e, if "parent" is -ve)
            countA = countB = 0
            while parent[potentialParentA] >= 0:
                potentialParentA = parent[potentialParentA]
                countA += 1
            parentA = potentialParentA
            countA += 1
            
            while parent[potentialParentB] >= 0:
                potentialParentB = parent[potentialParentB]
                countB += 1
            parentB = potentialParentB
            countB += 1
            # Now, we are sure that a parent has been found!

            # But wait, which parent has more weight? (see what I did there...)
            parentAweight = parent[parentA]
            parentBweight = parent[parentB]
            # comparing the magnitude (taking the abs since the parents have negative weight)
            if abs(parentAweight) >= abs(parentBweight): 
                parentA, parentB = parentA, parentB
                count = countB
                # ^ redundant but still paints a clear picture
            else:
                parentA, parentB = parentB, parentA
                count = countA
            # Note, parentA is set as the dominant weight

            if parentA != parentB:
                # Set parentA as the representative node
                parent[parentB] = parentA # setting parentB to map to parentA
                parent[parentA] -= count # -ve indicates A is parent and count indicates the # of children
            elif parentA == parentB:
                #print(f"A cycle has been formed between nodes {nodeA} and {nodeB}")
                self.alreadyConnectedEdges.append((nodeA, nodeB))


#### Using lists for checking connectivity 

    def generateKruskalGeneratedMaze(self):
        generateRandomPassages(self)
        print("edgesToAvoidConnecting", self.alreadyConnectedEdges)
        for (nodeA, nodeB) in self.passages:
            if (nodeA, nodeB) not in self.alreadyConnectedEdges:
                self.connectedGraph.addEdge(nodeA, nodeB)
        return self.connectedGraph

gridGraph = Graph()
connectedGraph = Graph()

for index in range(3*3): # looping through all the elements in the grid
    indexObj = Node(index, 3, 3)
    gridGraph.addNode(index) # add the index as a node in the graph
    NeighborLst = indexObj.getNeighbors() # returns a list of neighbors
    for neighbor in NeighborLst:
        # adds the neighbor as an edge to the index parent
        gridGraph.addEdge(index, neighbor)


generatedMaze = Kruskal(3, 3, gridGraph.graph, connectedGraph.graph)
print(generatedMaze.generateKruskalGeneratedMaze())
