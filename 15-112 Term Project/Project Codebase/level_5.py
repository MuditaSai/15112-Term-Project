from cmu_112_graphics import *
import copy, random
from node_class import *
from graph_class import * 
import pygame

# LEVEL 4: 
# LARGER MAZE
# POISON FEATURE: -5
# ENEMY DAMAGE: -20
# ENEMY COUNT: 3
# TIME LIMIT: 100s
# FASTER ENEMY

# Source: https://www.youtube.com/watch?v=z0aOffHrTac
# Reduces the time delay of the sound bite
pygame.mixer.pre_init(44100, -16, 2, 512)

counter = 0
rows = cols = dim = 25
numIndices = rows*cols
lstNodes = list(range(numIndices))

# Initializing a graph object that maps all the indices to their neighbors
gridGraph = Graph()
for index in range(rows*cols): # looping through all the elements in the grid
    indexObj = Node(index, rows, cols)
    gridGraph.addNode(index) # add the index as a node in the graph
    NeighborLst = indexObj.getNeighbors() # returns a list of neighbors
    for neighbor in NeighborLst:
        # adds the neighbor as an edge to the index parent
        gridGraph.addEdge(index, neighbor)

# Initializing a graph to be used by Kruskal's and Dijkstra's to produce a graph with ONLY the connected nodes
connectedGraph = Graph()

# Visualizing the graph
def visualizeGraph(g):
    for node in sorted(g.graph):
        sortedDict = dict(sorted(g.graph[node].items()))
        print(node, ":", sortedDict)
# visualizeGraph(g)

# Helpful helper function to convert between (row, col) --> node and node --> (row,col)
def nodeToRowColConverter(node, dim):
    row = node // dim
    col = node % dim
    return (row, col)

def rowColToNodeConverter(row, col, dim):
    node = (row*dim) + col
    return node

# Source: https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
def getCircleCenter(app, row, col):
    # aka "modelToView"
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = app.margin + col * cellWidth
    x1 = app.margin + (col+1) * cellWidth
    y0 = app.margin + row * cellHeight
    y1 = app.margin + (row+1) * cellHeight
    cx = (x0+x1) // 2
    cy = (y0+y1) // 2
    return (cx, cy)

# Source: https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
def getCellBounds(app, row, col):
    # aka "modelToView"
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth // app.cols
    cellHeight = gridHeight // app.rows
    x0 = app.margin + col * cellWidth
    x1 = app.margin + (col+1) * cellWidth
    y0 = app.margin + row * cellHeight
    y1 = app.margin + (row+1) * cellHeight
    return (x0, y0, x1, y1)

# Source: https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
# aka "viewToModel"
def getCell(app, x, y):
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth  = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    row = int((y - app.margin) / cellHeight)
    col = int((x - app.margin) / cellWidth)
    return (row, col)

# Source: https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#usingModes
def loadAnimatedGif(path):
    # load first sprite outside of try/except to raise file-related exceptions
    spritePhotoImages = [ PhotoImage(file=path, format='gif -index 0') ]
    i = 1
    while True:
        try:
            spritePhotoImages.append(PhotoImage(file=path,
                                                format=f'gif -index {i}'))
            i += 1
        except Exception as e:
            return spritePhotoImages

##### START OF MAZE ALGORITHMS #####

##### KRUSKAL'S IMPLEMENTATION ##### - MAZE GENERATION
# Pseudocode Inspiration: https://www.cs.cmu.edu/~112/notes/student-tp-guides/Mazes.pdf

# Returns a list of randomly shuffled node-neighbor tuples
def generateRandomPassages(g):
    result = []
    repeats = set()
    for node in g:
        t = tuple()
        for neighbor in g[node]:
            t = (node, neighbor)
            # Prevents tuples such as (1,0) and (0,1) both being added
            if t not in repeats:
                result.append(t)
            repeats.add((neighbor, node))
    # Destructively shuffles the list of tuples
    random.shuffle(result)
    return result

passages = generateRandomPassages(gridGraph.graph)

# Using a list to check connectivity 
def listConnectedEdges(passages, rows, cols):
    elems = rows*cols 
    parent = [-1]*elems
    alreadyConnectedEdges = [] # a list of already connected edges
    for (nodeA, nodeB) in passages:
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
            alreadyConnectedEdges.append((nodeA, nodeB))
    return alreadyConnectedEdges

def Kruskal(passages, rows, cols):
    edgesToAvoidConnecting = listConnectedEdges(passages, rows, cols)
    for (nodeA, nodeB) in passages:
        if (nodeA, nodeB) not in edgesToAvoidConnecting:
            connectedGraph.addEdge(nodeA, nodeB)
    # visualizeGraph(g1)
    return connectedGraph.graph

generatedMaze = Kruskal(passages, rows, cols)

##### DJIKSTRA'S IMPLEMENTATION ##### - PATHFINDING ALGO
# Pseudocode Inspiration: https://www.cs.cmu.edu/~112/notes/student-tp-guides/Pathfinding.pdf

# Returns the smallest node from the unvisited nodes
def getSmallestNode(g, visited):
    currLow = 999999
    currNode = None
    for node in g:
        if node not in visited:
            if (g[node] != None and g[node] < currLow):
                currLow = g[node]
                currNode = node
    return currNode

# Returns the list of the path leading from the source to the target 
# using a dictionary
def extractPath(g, source, target):
    result = [target]
    for elem in result:
        result.append(g[elem])
        if source in result:
            return list(reversed(result))

def Dijkstra(g, source, target):
    # g = Graph()
    # unvisited = g.getNodes()
    visited = set()
    unvisited = list(g)
    unvisited_copy = copy.copy(unvisited)
    dist = dict()
    prevDict = dict()

    # Initializing the distances of all the nodes from the start node
    for node in unvisited:
        # 0 for the start node
        if node == source:
            dist[node] = 0
        else:
            dist[node] = None # Analogous to setting distance to infinity
    # Algorithm runs till all the nodes have been visited
    while unvisited != []:
        # Just looping through all the nodes
        for node in unvisited_copy:
            # Returns the smallest unvisited node
            nodeToVisit = getSmallestNode(dist, visited)
            visited.add(nodeToVisit)
            for neighbor in g[nodeToVisit]:
                # Only visit the unvisited neighbors from the current node
                if neighbor not in visited:
                    weight = dist[nodeToVisit] # Weight of parent node
                    # Weight of parent + neighbor node
                    totalWeight = g[nodeToVisit][neighbor] + weight
                    # Total weight < Weight of current child weight
                    if dist[neighbor] == None or totalWeight < dist[neighbor]: 
                        # update child weight
                        dist[neighbor] = totalWeight
                        # ONLY UPDATE previous node if the distance is updated
                        prevDict[neighbor] = nodeToVisit
            unvisited.remove(nodeToVisit)
    return extractPath(prevDict, source, target)

##### END OF ALGORITHMS #####

# Initializing enemy start location:
randomStartLocationLst = list(range(1, numIndices))

def appStarted(app):
    # updateRowsCols(app)
    app.rows, app.cols = rows, cols
    app.margin = 50 # margin around grid
    app.cellSize = app.cellSize = (app.width - 2 * app.margin) //app.rows
    app.timerDelay = 100
    app.timerPassed = 0
    app.r = app.cellSize//2.5 

    # Defining player attributes
    app.playerX, app.playerY = getCircleCenter(app,0,0)
    app.direction = "Down"
    # Image source: https://www.deviantart.com/pizzasun/art/The-Flash-in-Style-of-Pokemon-Gen-4-Sprite-Sheet-680627315
    playerSpriteSheet = "flash.png"
    app.spriteSheet = app.loadImage(playerSpriteSheet)
    imageWidth, imageHeight = app.spriteSheet.size
    app.spriteSheet = app.scaleImage(app.spriteSheet, app.cellSize*4/imageWidth) 
    imageWidth, imageHeight = app.spriteSheet.size
    app.sprites = dict()
    for direction in ("Down0", "Left1", "Right2", "Up3"):
        index = int(direction[-1:])
        newDir = direction[:-1]
        topLefty = index * imageHeight / 4
        botRighty = (index+1) * imageHeight / 4
        tempSprites = []
        for j in range(4):
            topLeftx = j * imageWidth / 4
            botRightx = (j + 1) * imageHeight / 4
            sprite = app.spriteSheet.crop((topLeftx, topLefty, botRightx, botRighty))
            tempSprites.append(sprite)
        app.sprites[newDir] = tempSprites
        app.spriteCounter = 0

    # Defining enemy attributes
    # Initially enemy AI starts at the bottom right of the maze
    # Will change later to start at a random place that is not too clase to the player's starting position 
    tempSprites = []
    startPos = random.choice(randomStartLocationLst)
    app.enemyPath = [startPos]
    app.startPos = startPos
    app.finalPos = 0 # The node at which the player starts off at
    app.enemyCurrNode = app.startPos

    # Source: https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
    # Source: https://scs.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id=8a3ab4e2-c322-4f04-86e1-ae6a014ddc64
    app.enemyDirection = "Left"
    # Image source: https://www.deviantart.com/purplezaffre/art/Team-Plasma-Boss-Ghetsis-With-Staff-700980561
    enemySpriteSheet = "ghetsis.png"
    app.enemySpriteSheet = app.loadImage(enemySpriteSheet)
    enemImageWidth, enemImageHeight = app.enemySpriteSheet.size
    app.enemySpriteSheet = app.scaleImage(app.enemySpriteSheet, app.cellSize*4/enemImageWidth) 
    app.enemSprites = dict()
    enemImageWidth, enemImageHeight = app.enemySpriteSheet.size
    for direction in ("Down0", "Left1", "Right2", "Up3"):
        index = int(direction[-1:])
        newDir = direction[:-1]
        topLefty = index * enemImageHeight / 4
        botRighty = (index+1) * enemImageHeight / 4
        tempSprites = []
        for j in range(4):
            topLeftx = j * enemImageWidth / 4
            botRightx = (j + 1) * enemImageHeight / 4
            sprite = app.enemySpriteSheet.crop((topLeftx, topLefty, botRightx, botRighty))
            tempSprites.append(sprite)
        app.enemSprites[newDir] = tempSprites
        app.enemSpriteCounter = 0

    # Defining enemy attributes
    # Initially enemy AI starts at the bottom right of the maze
    # Will change later to start at a random place that is not too clase to the player's starting position 
    tempSprites = []
    startPos = random.choice(randomStartLocationLst)
    app.enemyTwoPath = [startPos]
    app.startTwoPos = startPos
    app.finalTwoPos = 0 # The node at which the player starts off at
    app.enemyTwoCurrNode = app.startTwoPos

    # have a function enemies to initialize the enemies, appStarted calls this function
    app.enemyTwoDirection = "Left"
    # Image source: https://www.deviantart.com/pizzasun/art/Redesigned-Giovanni-Gen-IV-Sprite-Sheet-714203072
    enemyTwoSpriteSheet = "giovanni.png"
    app.enemyTwoSpriteSheet = app.loadImage(enemyTwoSpriteSheet)
    enemTwoImageWidth, enemTwoImageHeight = app.enemyTwoSpriteSheet.size
    app.enemyTwoSpriteSheet = app.scaleImage(app.enemyTwoSpriteSheet, app.cellSize*4/enemTwoImageWidth) 
    app.enemTwoSprites = dict()
    enemTwoImageWidth, enemTwoImageHeight = app.enemyTwoSpriteSheet.size
    for direction in ("Down0", "Left1", "Right2", "Up3"):
        index = int(direction[-1:])
        newDir = direction[:-1]
        topLefty = index * enemTwoImageHeight / 4
        botRighty = (index+1) * enemTwoImageHeight / 4
        tempSprites = []
        for j in range(4):
            topLeftx = j * enemTwoImageWidth / 4
            botRightx = (j + 1) * enemTwoImageHeight / 4
            sprite = app.enemyTwoSpriteSheet.crop((topLeftx, topLefty, botRightx, botRighty))
            tempSprites.append(sprite)
        app.enemTwoSprites[newDir] = tempSprites
        app.enemTwoSpriteCounter = 0

    # Defining enemy attributes
    # Initially enemy AI starts at the bottom right of the maze
    # Will change later to start at a random place that is not too clase to the player's starting position 
    tempSprites = []
    startPos = random.choice(randomStartLocationLst)
    app.enemyThreePath = [startPos]
    app.startThreePos = startPos
    app.finalThreePos = 0 # The node at which the player starts off at
    app.enemyThreeCurrNode = app.startThreePos

    # have a function enemies to initialize the enemies, appStarted calls this function
    app.enemyThreeDirection = "Left"
    enemyThreeSpriteSheet = "giovanni.png"
    app.enemyThreeSpriteSheet = app.loadImage(enemyThreeSpriteSheet)
    enemThreeImageWidth, enemThreeImageHeight = app.enemyThreeSpriteSheet.size
    app.enemyThreeSpriteSheet = app.scaleImage(app.enemyThreeSpriteSheet, app.cellSize*4/enemThreeImageWidth) 
    app.enemThreeSprites = dict()
    enemThreeImageWidth, enemThreeImageHeight = app.enemyThreeSpriteSheet.size
    for direction in ("Down0", "Left1", "Right2", "Up3"):
        index = int(direction[-1:])
        newDir = direction[:-1]
        topLefty = index * enemThreeImageHeight / 4
        botRighty = (index+1) * enemThreeImageHeight / 4
        tempSprites = []
        for j in range(4):
            topLeftx = j * enemThreeImageWidth / 4
            botRightx = (j + 1) * enemThreeImageHeight / 4
            sprite = app.enemyThreeSpriteSheet.crop((topLeftx, topLefty, botRightx, botRighty))
            tempSprites.append(sprite)
        app.enemThreeSprites[newDir] = tempSprites
        app.enemThreeSpriteCounter = 0

    app.colorLst = ["turquoise1", "turquoise2", "turquoise3", "cyan2", "cyan3"]
    app.color = "turquoise1"


    # Initializing the exit graphic
    # Image source: https://oldschoolrunescape.fandom.com/wiki/Dungeon_entrance
    app.exitImage = app.loadImage('entrance.png')
    app.exitImage = app.scaleImage(app.exitImage, 0.1)

    # Initializing the food list:
    allNodes = [i for i in range(numIndices)]
    nodesToAvoid = random.sample(allNodes, numIndices - dim)
    rowColToAvoid = []

    for node in nodesToAvoid:
        row, col = nodeToRowColConverter(node, dim)
        rowColToAvoid.append((row,col))

    foodLst = []
    for row in range(rows):
        for col in range(cols):
            if (row, col) not in rowColToAvoid:
                foodLst.append((row,col))

    app.foodR = app.r//2 
    app.foodLst = foodLst
    app.foodColor = "yellow"
    app.setColor = app.foodColor

    # Initializing legal move for the player
    app.canMoveLeft = None
    app.canMoveRight = None
    app.canMoveUp = None
    app.canMoveDown = None

    # Initally, no path is drawn to help the player
    app.canDrawPath = False
    # Initially, the game is unpaused
    app.isPaused = False

    app.score = 100
    app.time = 100

    # Initializing a bunch of screens/modes

    # Initialzing the splash screen screen
    # Image source: https://www.freepik.com/free-vector/turing-pattern-structure-organic-lines-background-design_10016725.htm#query=organic%20pattern&position=0&from_view=keyword
    app.backgroundImg = app.loadImage("greenmaze.png")
    app.backgroundImg = app.scaleImage(app.backgroundImg, 2)

    # Initializing the end game screen
    # Image source: https://in.pinterest.com/pin/128423026861195977/
    app.endGameImage = app.loadImage('end_screen.gif')
    app.endGameImage = app.scaleImage(app.endGameImage, 2)

    # Initializing the end credits screen
    # Image source: https://tenor.com/view/fortnitepokemon-gif-25023770
    app.endCreditsImage = app.loadImage('pog.gif')
    app.endCreditsImage = app.scaleImage(app.endCreditsImage, 2)

    # Splash screen is the default screen
    app.mode = 'gameMode'

# Maps the output of Kruskal's onto a grid
def f(g1, dim, numIndices, node):

    allNeighbors = []

    # Add all the valid neighbors of the index
    leftNode = node - 1
    allNeighbors.append(leftNode)

    topNode = node - dim
    allNeighbors.append(topNode)

    rightNode = node + 1
    allNeighbors.append(rightNode)

    bottomNode = node + dim
    allNeighbors.append(bottomNode)

    actualNeighborLst = g1.getConnectedNodesWeighted(node)

    drawLst = []

    # drawLst: 1 = draw border and 0 = don't draw border
    for neighbor in allNeighbors:
        if neighbor not in actualNeighborLst:
            drawLst.append(1)
        else:
            drawLst.append(0)
    return drawLst

# Helper for drawGrid
# Source: My tetris code from autolab -- https://autolab.andrew.cmu.edu/courses/15112-s22/assessments/hw6/submissions/7811466/view
def drawCell(app, canvas, row, col, node, connectedGraph):
    x1 = app.margin + col*app.cellSize
    x2 = app.margin + (col+1)*app.cellSize
    y1 = app.margin + row*app.cellSize
    y2 = app.margin + (row+1)*app.cellSize

    drawLst = f(connectedGraph, dim, numIndices, node)

    leftEdge = drawLst[0]
    topEdge = drawLst[1]
    rightEdge = drawLst[2]
    bottomEdge = drawLst[3]

    # Left 
    if leftEdge == 1:
        canvas.create_rectangle(x1, y1, x1, y2, outline = app.color)

    # Top
    if topEdge == 1:
        canvas.create_rectangle(x1, y1, x2, y1, outline = app.color)

    # Bottom
    if bottomEdge == 1:
        canvas.create_rectangle(x1, y2, x2, y2, outline = app.color)

    # Right
    if rightEdge == 1:
        canvas.create_rectangle(x2, y1, x2, y2, outline = app.color)

def drawGrid(app,canvas):
    nodeIndx = -1
    for row in range(app.rows):
        for col in range(app.cols):
            nodeIndx += 1
            drawCell(app, canvas, row, col, nodeIndx, connectedGraph)

def updateLegalMove(app, row, col, dim):
    node = rowColToNodeConverter(row, col, dim)
    drawLst = f(connectedGraph, dim, numIndices, node)

    leftEdge = drawLst[0]
    topEdge = drawLst[1]
    rightEdge = drawLst[2]
    bottomEdge = drawLst[3]

    # Left 
    if leftEdge == 1: app.canMoveLeft = False 
    else: app.canMoveLeft = True

    # Top
    if topEdge == 1: app.canMoveUp = False
    else: app.canMoveUp = True

    # Bottom
    if bottomEdge == 1: app.canMoveDown = False
    else: app.canMoveDown = True

    # Right
    if rightEdge == 1: app.canMoveRight = False
    else: app.canMoveRight = True

dirs = ["Left", "Right", "Up", "Down"]
itemColorLst = ["yellow", "purple"]
def timerFired(app):

    if app.time == 0:
        app.showMessage("Time's up!")
        app.mode = "gameOverMode"

    if app.score <= 0:
        app.showMessage("You took too much damage!")
        app.mode = "gameOverMode"

    if not app.isPaused:

        # Update the enemy's current location
        app.enemyCurrNode = app.enemyPath[0]
        app.enemyTwoCurrNode = app.enemyTwoPath[0]
        app.enemyThreeCurrNode = app.enemyThreePath[0]
        # Randomly change the enemy's direction (creating a "rotation effect")
        app.enemyDirection = random.choice(dirs)
        app.enemyTwoDirection = random.choice(dirs)
        app.enemyThreeDirection = random.choice(dirs)
        # update the player's sprite animation in regular time intervals
        app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
        # change the color of the grid in regular time intervals
        app.color = random.choice(app.colorLst)

        app.timerPassed += app.timerDelay

        if app.timerPassed % 2000 == 0:
            # Randomly posion all the food at any given moment
            app.foodColor = random.choices(itemColorLst, weights = (90, 10), k = 1)
            app.setColor = app.foodColor[0]
            print("app.setColor", app.setColor)

        if app.timerPassed % 1000 == 0:
            # Decreasing time every second
            app.time -= 1
        if app.timerPassed % 50 == 0:
            # Once enough time has passed do the following:
            # 1. Move the enemy
            # 2. Pop the first node in the list and replace it instantly by the 
            # next node in the list
            if app.startPos != app.finalPos:
                enemyTakeStep(app)
                if len(app.enemyPath) > 0:
                    app.enemyPath.pop(0)
                app.startPos = app.enemyPath[0]
            
            enemyTwoTakeStep(app)
            if len(app.enemyTwoPath) > 0:
                app.enemyTwoPath.pop(0)
            # The new start position of the enemy is the current 0th index
            app.startTwoPos = app.enemyTwoPath[0]

            enemyThreeTakeStep(app)
            if len(app.enemyThreePath) > 0:
                app.enemyThreePath.pop(0)
            # The new start position of the enemy is the current 0th index
            app.startThreePos = app.enemyThreePath[0]


def enemyTakeStep(app):
    app.enemyPath = Dijkstra(generatedMaze, app.startPos, app.finalPos)

def enemyTwoTakeStep(app):
    app.enemyTwoPath = Dijkstra(generatedMaze, app.startTwoPos, app.finalTwoPos)

def enemyThreeTakeStep(app):
    app.enemyThreePath = Dijkstra(generatedMaze, app.startThreePos, app.finalThreePos)

def drawEnemy(app, canvas):  
    # Enemy path is constantly updated 
    # The starting position is the enemy's current location
    # The final destination is the player's current location
    node = app.enemyPath[0]
    row, col = nodeToRowColConverter(node, dim)
    x0, y0, x1, y1 = getCellBounds(app, row, col)
    x = (x0 + x1) / 2 
    y = (y0 + y1) / 2
    sprite = app.enemSprites[app.enemyDirection][app.enemSpriteCounter]
    canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))

def drawEnemyTwo(app, canvas):  
    # Enemy path is constantly updated 
    # The starting position is the enemy's current location
    # The final destination is the player's current location
    node = app.enemyTwoPath[0]
    row, col = nodeToRowColConverter(node, dim)
    x0, y0, x1, y1 = getCellBounds(app, row, col)
    x = (x0 + x1) / 2 
    y = (y0 + y1) / 2
    sprite = app.enemTwoSprites[app.enemyTwoDirection][app.enemTwoSpriteCounter]
    canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))

def drawEnemyThree(app, canvas):  
    # Enemy path is constantly updated 
    # The starting position is the enemy's current location
    # The final destination is the player's current location
    node = app.enemyThreePath[0]
    row, col = nodeToRowColConverter(node, dim)
    x0, y0, x1, y1 = getCellBounds(app, row, col)
    x = (x0 + x1) / 2 
    y = (y0 + y1) / 2
    sprite = app.enemThreeSprites[app.enemyThreeDirection][app.enemThreeSpriteCounter]
    canvas.create_image(x, y, image=ImageTk.PhotoImage(sprite))


def movePlayer(app, dx, dy):
    app.spriteCounter = (app.spriteCounter + 1) % 4
    app.isMoving = True
    app.playerX += dx
    app.playerY += dy

def keyPressed(app, event):
    # If the user presses c, display the shortest path to the exit from their current location by using Dijkstra's algo
    if event.key == "c":
        app.score -= 20
        app.canDrawPath = not app.canDrawPath

    if event.key == "p":
        app.isPaused = not app.isPaused
    
    if event.key == "r":
        appStarted(app)

    if not app.isPaused:
        row, col = getCell(app, app.playerX, app.playerY)
        currNode = rowColToNodeConverter(row, col, dim) 
        # Checking if the updated row and updated col are valid by checking if the respective node at that position is valid
        if currNode in range(rows*cols):
        # Update the 4 booleans based on the current row-col position
            updateLegalMove(app, row, col, dim)

            if (event.key == 'Left'):
                if app.canMoveLeft:
                    movePlayer(app, -app.cellSize, 0)
                    app.direction = event.key

            if (event.key == 'Right'):
                if app.canMoveRight:
                    movePlayer(app, app.cellSize, 0)
                    app.direction = event.key

            if (event.key == 'Up'):
                if app.canMoveUp:
                    movePlayer(app, 0, -app.cellSize)
                    app.direction = event.key

            if (event.key == 'Down'):
                if app.canMoveDown:
                    movePlayer(app, 0, app.cellSize)
                    app.direction = event.key

       # Removing food when the player makes contact with the food!
        # Update score if food is eaten by player
        # playerRow, playerCol = getCell(app, app.cx, app.cy)
        playerRow, playerCol = getCell(app, app.playerX, app.playerY)
        playerNode = rowColToNodeConverter(playerRow, playerCol, dim)

        # If the player reaches the bottom right corner (reaches the exit)
        if playerNode == numIndices - 1 and app.foodLst != []:
            app.showMessage("Collect all items before moving on to the next level!")
        elif playerNode == numIndices - 1 and app.foodLst == []:
            app.mode = "creditsMode"

        if (playerRow, playerCol) in app.foodLst and app.setColor == "yellow":
            app.foodLst.remove((playerRow, playerCol))
            if app.score + 5 <= 100:
                app.score += 5
            # Play healing sounds if player comes into contact with food 
            # Source: https://stackoverflow.com/questions/7746263/how-can-i-play-an-mp3-with-pygame
            pygame.init()
            pygame.mixer.init()
            # Audio source: https://www.youtube.com/watch?v=aSc9LL-i08M
            pygame.mixer.music.load("heal_sound.wav")
            pygame.mixer.music.play()

        elif (playerRow, playerCol) in app.foodLst and app.setColor == "purple":
            app.foodLst.remove((playerRow, playerCol))
            app.score -= 5
            # Play poisoned sounds if player comes into contact with food 
            # Source: https://stackoverflow.com/questions/7746263/how-can-i-play-an-mp3-with-pygame
            pygame.init()
            pygame.mixer.init()
             # Audio source: https://www.youtube.com/watch?v=55mc_Gi27t4
            pygame.mixer.music.load("player_taking_damage.wav")
            pygame.mixer.music.play()
            

        row, col = getCell(app, app.playerX, app.playerY)
        currPlayerNode = rowColToNodeConverter(row, col, dim) 

        # Decrease player's score if they come into contact with an enemy
        if app.enemyCurrNode == currPlayerNode or app.enemyTwoCurrNode == currPlayerNode or app.enemyThreeCurrNode == currPlayerNode:
            app.score -= 20
             # Play damage sounds if player comes into contact with an enemy
            # Source: https://stackoverflow.com/questions/7746263/how-can-i-play-an-mp3-with-pygame
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load("player_taking_damage.wav")
            pygame.mixer.music.play()

        # Need to update finalPos
        app.finalPos = currPlayerNode
        nextPos = random.choice(lstNodes)
        if nextPos != app.startTwoPos:
            app.finalTwoPos = nextPos
        nextNextPos = random.choice(lstNodes)
        if nextNextPos != app.startThreePos:
            app.finalThreePos = nextPos
        
        
def drawPlayer(app,canvas):
    sprite = app.sprites[app.direction][app.spriteCounter]
    canvas.create_image(app.playerX, app.playerY, image=ImageTk.PhotoImage(sprite))

def drawFood(app, canvas):
    for row, col in app.foodLst:
        x0, y0, x1, y1 = getCellBounds(app, row, col)
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        canvas.create_oval(cx-app.foodR, cy-app.foodR, cx+app.foodR, cy+app.foodR, fill = "yellow")

def drawDungeon(app, canvas):
    row, col = nodeToRowColConverter(numIndices - 1, dim)
    x, y = getCircleCenter(app, row, col)
    canvas.create_image(x, y, image=ImageTk.PhotoImage(app.exitImage))

def drawLevel(app, canvas):
    canvas.create_text(app.width/2, 30, text = "Level: 4", font = 'Phosphate 30 bold')

def drawScore(app, canvas):
    # Actual outline
    canvas.create_rectangle(app.width - 200, 20, app.width - 2*app.margin, 40, fill = "green", outline = "black")
    # Effect of decreasing the HP
    if app.score > 0:
        canvas.create_rectangle(app.width - 2*app.margin - 100 + app.score, 20, app.width - 2*app.margin, 40, fill = "white")
    # Effect of increasing the HP
    if app.score <= 100 and app.score != 0:
        canvas.create_rectangle(app.width - 200, 20, app.width - 2*app.margin - 100 + app.score, 40, fill = "green")
    # Displaying the score
    canvas.create_text(((app.width - 200) + (app.width - 2*app.margin))/2, 30, text = f"HP: {app.score}", fill = "black", font = "Arial 10 bold")

def drawTimeLimit(app, canvas):
    canvas.create_rectangle(app.margin*2, 20, app.margin*2 + 100, 40, fill = "white", outline = "black")
    # Effect of decreasing the time
    canvas.create_rectangle(app.margin*2, 20, app.margin*2 + app.time, 40, fill = "green")
    canvas.create_text(((app.margin*2) + (app.margin*2 + 100))/2, 30, text = f"Time: {app.time}", fill = "black", font = "Arial 10 bold")

# Draws a path from the players current position to the exit
def drawPath(app, canvas):
    playerRow, playerCol = getCell(app, app.playerX, app.playerY)
    playerNode = rowColToNodeConverter(playerRow, playerCol, dim)

    # Find a path from the player's current position to the bottom right of the 
    # maze using the output from Kruskal's
    path = Dijkstra(generatedMaze, playerNode, (rows*cols) - 1)

    for node in path:
        row, col = nodeToRowColConverter(node, dim)
        x0, y0, x1, y1 = getCellBounds(app, row, col)
        canvas.create_rectangle(x0, y0, x1, y1, fill = "red")

def drawBackgroundGrid(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            x0, y0, x1, y1 = getCellBounds(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1, fill = "black")

def redrawAll(app, canvas):
    drawBackgroundGrid(app,canvas)
    drawGrid(app,canvas)
    drawFood(app, canvas)
    drawPlayer(app,canvas)
    drawScore(app, canvas)
    drawTimeLimit(app, canvas)
    drawLevel(app, canvas)
    if app.canDrawPath:
        drawPath(app, canvas)
    drawEnemy(app, canvas)
    drawEnemyTwo(app, canvas)
    drawEnemyThree(app, canvas)
    drawDungeon(app, canvas)

# Source for using modes: https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html

##########################################
# Splash Screen Mode
##########################################

def splashScreenMode_redrawAll(app, canvas):
    font = 'Phosphate 30 bold'
    # photoImage = app.spritePhotoImages[app.spritesSplashCounter]
    # canvas.create_image(200, 200, image=photoImage)
    canvas.create_image(700, 700, image=ImageTk.PhotoImage(app.backgroundImg))

    canvas.create_text(app.width/2, 150, text='Welcome to the Escaparoo Mazaroo!',
                    font=font, fill='black')
    canvas.create_rectangle(app.width/4 - 50, 200, app.width/2 - 50, 250, fill = "red")
    canvas.create_text(((app.width/4 - 50) + (app.width/2 - 50))/2, 450/2, text = "Play", font = "Phosphate 20")
    canvas.create_rectangle(app.width/2 + 50, 200, (app.width/1.5) + 100, 250, fill = "orange")
    canvas.create_text(((app.width/2 + 50) + ((app.width/1.5) + 100))/2, 450/2, text = "Help", font = "Phosphate 20")

def splashScreenMode_mousePressed(app, event):
    if ((app.width/4 - 50 <= event.x <= app.width/2 - 50) and (200 <= event.y <= 250)):
        app.mode = "gameMode"
    elif ((app.width/2 + 50 <= event.x <= (app.width/1.5) + 100) and (200 <= event.y <= 250)):
        app.mode = "helpMode"

##########################################
# Game Mode
##########################################

def gameMode_redrawAll(app, canvas):
    redrawAll(app, canvas)

def gameMode_timerFired(app):
    timerFired(app)

def gameMode_keyPressed(app, event):
    keyPressed(app, event)
    if event.key == "h":
        app.mode = "helpMode"

##########################################
# Help Mode
##########################################

def helpMode_redrawAll(app, canvas):
    font = 'Skia 30 bold'
    canvas.create_text(app.width/2, 50, text='Mission', 
                       font=font, fill='black')
    canvas.create_text(app.width/2, 200, 
    text="Shoot, your airship crashed onto an unknown planet and you are nowhere near the airship. Your mission is to traverse through a set of 5 mazes, each with increasing difficulty to reach to the other side. But beware, enemies lie in every nook and cranny. Avoid enemies and stock up on food. Good luck soldier!",
                       font=font, fill='purple', width = app.width - 10)

    canvas.create_text(app.width/2, 350, 
    text="Commands",font=font, fill='black', width = app.width - 10)
    canvas.create_text(app.width/2, 450, 
    text="Control the character by: up, down, left, right. Press p to pause. Press h to toggle between gameplay and the help pane. Press r to reset level. Press c to enable cheat, but do so at your own risk as you will lose points...",font=font, fill='purple', width = app.width - 10)

    canvas.create_rectangle((app.width/2) - 100, 550, (app.width/2) + 100, 600, fill = "cyan")
    canvas.create_text(((app.width/2 - 100) + ((app.width/2) + 100))/2, 1150/2, text = "Menu", font = "Phosphate 20 bold")

def helpMode_keyPressed(app, event):
    if event.key == "h":
        app.mode = "gameMode"

def helpMode_mousePressed(app, event):
    if (((app.width/2 - 100) <= event.x <= (app.width/2 + 100)) and (550 <= event.y <= 600)):
        app.mode = "splashScreenMode"

##########################################
# Game Over
##########################################

def gameOverMode_redrawAll(app, canvas):
    font = 'Skia 30 bold'
    canvas.create_image(200, 300, image=ImageTk.PhotoImage(app.endGameImage))
    # photoImage = app.endGameImage[app.endGamespriteCounter]
    # canvas.create_image(400, 400, image=photoImage)
    canvas.create_text(app.width/2, 150, text='Game Over!', 
                       font=font, fill='Orange')
    canvas.create_rectangle(app.width/2 - 100, 400, app.width/2 + 100, 450, fill = "orange")
    canvas.create_text(((app.width/2 - 100)+(app.width/2 + 100)) / 2,  850/2, text = "Menu", font = "Phosphate 20 bold")


def gameOverMode_mousePressed(app, event):
    if ((app.width/2 - 100 <= event.x <= app.width/2 + 100) and (400 <= event.y <= 450)):
        # Resetting to level 1
        # Source inspiration: https://stackoverflow.com/questions/61843030/how-to-use-one-python-script-to-run-another-python-script-and-pass-variables-to
        import level_1
        execfile('level_1.py')
        app.mode = "splashScreenMode"

##########################################
# End Credits
##########################################

def creditsMode_redrawAll(app, canvas):
    font = 'Phosphate 30 bold'
    canvas.create_image(200, 300, image=ImageTk.PhotoImage(app.endCreditsImage))
    canvas.create_text(app.width/2, 350, text="Congratulations!!!",
                       font=font, fill='purple')
    app.mode = "splashScreenMode"

runApp(width=700, height=700)
