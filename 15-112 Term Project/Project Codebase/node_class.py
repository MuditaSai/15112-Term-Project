# Defining Node methods
class Node():
    def __init__(self, index, numRows, numCols):
        self.node = []
        self.index = index
        self.width = 30
        self.height = 30
        self.x = 100
        self.y = 100 
        self.row = index//numRows
        self.col = index%numRows
        self.numRows = numRows
        self.numCols = numCols

    def getIndex (self):
        return self.index

    def position(self):
        return (self.x, self.y)

    def rowAndCol(self):
        return (self.row, self.col)

    @staticmethod
    def isLegalRowCol(numRows, numCols, row, col):
        if (0 <= row < numRows) and (0 <= col < numCols):
            return True
        return False

    # Returns a list of the horizontal and vertical neighbors of a node
    def getNeighbors(self):

        #upper neighbor
        neighborArow = self.row - 1
        neighborAcol = self.col
        
        #lower neighbor
        neighborBrow = self.row + 1
        neighborBcol = self.col
        
        #left neighbor
        neighborCrow = self.row
        neighborCcol = self.col - 1
        
        #right neighbor
        neighborDrow = self.row
        neighborDcol = self.col + 1

        listIndex = []
        finalIndx = []

        if Node.isLegalRowCol(self.numRows, self.numCols, neighborArow, neighborAcol):
            indexA = neighborArow*self.numCols + neighborAcol
            listIndex.append(indexA)

        if Node.isLegalRowCol(self.numRows, self.numCols, neighborBrow, neighborBcol):
            indexB = neighborBrow*self.numCols + neighborBcol
            listIndex.append(indexB)
            
        if Node.isLegalRowCol(self.numRows, self.numCols, neighborCrow, neighborCcol):
            indexC = neighborCrow*self.numCols + neighborCcol
            listIndex.append(indexC)

        if Node.isLegalRowCol(self.numRows, self.numCols, neighborDrow, neighborDcol):
            indexD = neighborDrow*self.numCols + neighborDcol
            listIndex.append(indexD)

        for indx in listIndex:
            if ((indx//self.numRows) >= 0) and ((indx//self.numRows) < self.numRows):
                if ((indx%self.numRows) >= 0) and ((indx%self.numRows) < self.numCols):
                     finalIndx.append(indx)
        return finalIndx