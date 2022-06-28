from cmu_112_graphics import *


class Player:
    
def appStarted(app):
    app.playerX = 0
    app.playerY = 0
    app.direction = "Left"
    playerSpriteSheet = "colress.png"
    app.spriteSheet = app.loadImage(playerSpriteSheet)
    app.sprites = dict()
    imageWidth, imageHeight = app.spriteSheet.size
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

def movePlayer(app, dx, dy):
    print(app.playerX, app.playerY)
    app.spriteCounter = (app.spriteCounter + 1) % 4
    app.isMoving = True
    app.playerX += dx
    app.playerY += dy

def keyPressed(app, event):
    if event.key == "Left":
        movePlayer(app, -15, 0)
        app.direction = event.key
    if event.key == "Right":
        movePlayer(app, +15, 0)
        app.direction = event.key
    if event.key == "Up":
        movePlayer(app, 0, -15)
        app.direction = event.key
    if event.key == "Down":
        movePlayer(app, 0, +15)
        app.direction = event.key
    else:
        pass

    # for i in range(6):
    #     sprite = spritestrip.crop((86+89*i, 30, 200+26*i, 250))
    #     app.sprites.append(sprite)
    # app.spriteCounter = 0

def timerFired(app):
    app.spriteCounter = (1 + app.spriteCounter) % len(app.sprites)
    print(app.spriteCounter)
    

def redrawAll(app, canvas):
    sprite = app.sprites[app.direction][app.spriteCounter]
    canvas.create_image(app.playerX, app.playerY, image=ImageTk.PhotoImage(sprite))

runApp(width=400, height=400)
