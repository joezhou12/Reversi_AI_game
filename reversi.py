from tkinter import *
from tkinter.font import Font
from time import sleep
from random import choice


# global varsa
difficultyLevel = 0
userTurn = True
realUserTurn = True
playerClr = "black"
computerClr = "white"

widthOfBox = 62.5
board = []
boxesBoard = []
gameCanvas = any
playerCount = 0
computerCount = 0
playerCountIntVar = any
computerCountIntVar = any
gameCanvasWindow = any
indicator = None

gameMessage = any

gameFinished = False

# to update score board 
def updateScore():
    global playerCount, computerCount
    playerCount = 0
    computerCount = 0
    for row in board:
        for clr in row:
            if clr == "white":
                computerCount += 1
            elif clr == "black":
                playerCount += 1
    playerCountIntVar.set(playerCount)
    computerCountIntVar.set(computerCount)
    pass


# check if move is valid
def checkifValidmove(x,y,clr):
    #If spot is not empty, it's an invalid move
    if board[x][y]!=None:
        return False

    else:
        #checking adjacent blocks
        adjacent = False
        adjacents = []
        for i in range(max( 0 , x - 1 ), min( x + 2 , 8 )):
            for j in range(max( 0 , y-1 ), min( y + 2 , 8 )):
                if board[i][j]!=None:
                    adjacent=True
                    adjacents.append([i,j])
        #If there's no adjacent nodes move is invalid
        if not adjacent:
            return False
        else:
            #checking all adjacent nodes if there is any valid move
            valid = False
            for adjacent in adjacents:
                tempAdjX = adjacent[0]
                tempAdjY = adjacent[1]
                #if the color of the node is similar move is not valid
                #check next node
                if board[tempAdjX][tempAdjY]==clr:
                    continue
                else:
                    #get the direction
                    changeInX = tempAdjX-x
                    changeInY = tempAdjY-y
                    tempX = tempAdjX
                    tempY = tempAdjY

                    while 0 <= tempX <= 7 and 0 <= tempY <= 7:
                        #if the block between is empty
                        if board[tempX][tempY]==None:
                            break
                        #if finds opponents block move is valid
                        if board[tempX][tempY] == clr:
                            valid = True
                            break
                        tempX = tempX + changeInX   #update indexes towards direction

                        tempY = tempY + changeInY   #update indexes towards direction
            return valid
    pass

def playGame():
    global userTurn, userTurnName, gameFinished, gameMessage
    if not gameFinished:
#         run until computers turn and user cannot move
        while ( not userTurn and userCanPlay(computerClr) ):
#             select algorithm according to the selection
            if difficultyLevel == 0:    #easy mode
                easyAi()
            else:   #hard mode
                hardAi()

            if userCanPlay(playerClr):
                userTurn = True
            else:
#                 user don't have any move so its turn is skipped
                sleep(1)
                
#         if both players cannot move the game is over
        if(not userCanPlay(playerClr) and not userCanPlay(computerClr)):
            gameFinished = True
            announceWinner()
    else:
        announceWinner()
    
    pass


def announceWinner():
    #update the score board before checking and update the label variable
    updateScore()
    msg = ""
    if playerCount > computerCount:
        msg = "Player Won"
    elif playerCount == computerCount:
        msg = "Match Tied"
    else:
        msg = "Computer Won"
        
    gameMessage.set(msg)
        
    pass

def move(x,y,clr):
    global board
    #color clicked or selected block and update array
    board[x][y] = clr   
    borderBox = gameCanvas.coords(boxesBoard[x][y])
    #2 is padding between oval and contained rectangle
    gameCanvas.create_oval(borderBox[0]+2, borderBox[1]+2, borderBox[2]-2,borderBox[3]-2, fill=clr, outline="")
    latestIndicator(borderBox[0], borderBox[1], borderBox[2],borderBox[3])
    
    #listing all adjacent nodes
    adjacents = []
    for i in range(max(0,x-1),min(x+2,8)):
        for j in range(max(0,y-1),min(y+2,8)):
            if board[i][j]!=None:
                adjacents.append([i,j])
    
    #blocks to update
    alterdArray = []
    #for each adjacent node check which direction/s it can turn blocks
    for adjacent in adjacents:
        tempAdjX = adjacent[0]
        tempAdjY = adjacent[1]
        #Check if the adjacent node have different colour - form a line
        if board[tempAdjX][tempAdjY]!=clr:
            #for each formed line between adjecent nodes add the in between nodes
            lineToUpdate = []
            
            #Determining direction to move
            changeInX = tempAdjX-x
            changeInY = tempAdjY-y
            tempY = tempAdjY
            tempX = tempAdjX

            #stay in the board bounds -- 8 x 8
            while 0 <= tempX <= 7 and 0 <= tempY <= 7:
                lineToUpdate.append([tempX,tempY])
                value = board[tempX][tempY]
                if value==None: #if empty block is found line ends there
                    break
                if value==clr:  #If opponent's block is hit then there's the line to update
                    for node in lineToUpdate:
                        alterdArray.append(node)
                    break
                #update index's towards direction
                tempX = tempX + changeInX
                tempY = tempY + changeInY
                
    #update all the opponents blocks to the clr  and update array
    for pos in alterdArray:
        board[pos[0]][pos[1]]=clr
        borderBox = gameCanvas.coords(boxesBoard[pos[0]][pos[1]])
        gameCanvas.create_oval(borderBox[0]+2, borderBox[1]+2, borderBox[2]-2,borderBox[3]-2, fill=clr, outline="")
        
#     update scores
    updateScore()

    
    pass


# find a valid move if found one move there else pass

def easyAi():
    listOfValidMoves = []
    for i in range(8):
        for j in range(8):
            if checkifValidmove(i, j, computerClr):
                listOfValidMoves.append((i,j))
    
    randomMove = choice(listOfValidMoves)
    move(randomMove[0], randomMove[1], computerClr)
    
    pass

# algorithm: local maximization
# get all the valid moves and compare them if any position have high value update maximum points and move to that location
def hardAi():
#     reward table to reference which position have high reward
    rewardTable = [[100,-20,10,5,5,10,-20,100],
                   [-20,-50,-2,-2,-2,-2,-50,-20],
                   [10,-2,-1,-1,-1,-1,-2,10],
                   [5,-2,-1,-1,-1,-1,-2,5],
                   [5,-2,-1,-1,-1,-1,-2,5],
                   [10,-2,-1,-1,-1,-1,-2,10],
                   [-20,-50,-2,-2,-2,-2,-50,-20],
                   [100,-20,10,5,5,10,-20,100]]
    
#     set maximum to -1 *reward
    maximumPoints = (2,2)
    tempVals = (0,0)
    global computerClr
    
    for i in range(8):
        for j in range(8):
            if checkifValidmove(i, j, computerClr):
                if(rewardTable[i][j] >= rewardTable[maximumPoints[0]][maximumPoints[1]]):
                    maximumPoints = i,j
                else:
                    tempVals = i,j
    
#     if valid maximum points found move to that index else move to the valid move else pass
    if(checkifValidmove(maximumPoints[0], maximumPoints[1], computerClr)):
        move(maximumPoints[0], maximumPoints[1], computerClr)
    elif(checkifValidmove(tempVals[0], tempVals[1], computerClr)):
        move(tempVals[0], tempVals[1], computerClr)
    
    pass

def userCanPlay(clr):
#     check if there is any possible moves
    for x in range(8):
        for y in range(8):
            if checkifValidmove(x, y, clr):
                return True
    return False

# get the x-axis and y-axis from the click listener and proceed to next step -- move if possible
def mouseClickListener(event):
    global userTurn, gameFinished
    if not gameFinished:
        if userTurn and userCanPlay(playerClr):
            xMouse = event.x
            yMouse = event.y
            xPosition = int(xMouse//widthOfBox)
            yPosition = int(yMouse//widthOfBox)
            if(checkifValidmove(yPosition, xPosition, playerClr)):
                move(yPosition, xPosition, playerClr)
                if userCanPlay(computerClr):
                    userTurn = False
        if not userTurn:
            playGame()
            
        if(not userCanPlay(playerClr) and not userCanPlay(computerClr)):
            gameFinished = True
            announceWinner()
    else:
        announceWinner()
    pass


#reset game
def resetGame():
    global board, gameMessage, boxesBoard, gameFinished
    global gameCanvas
    del board[:]    #delete all previous elements in the array
    board = [ [None]*8  for n in range(8)] # list comprehension
    del boxesBoard[:]   #delete all previous elements in the array
    gameCanvas.delete("all")    #delete all canvas objects
    gameMessage.set("") #remove game message if any
    gameFinished = False #if game is finished then make it false because game is restarted
    drawReversiBoard()  #draw game board again
    userTurn = realUserTurn
    if not userTurn:    #start game with previously selected player
        gameCanvas.after(200, playGame)
    
    pass

# initialize all variables and canvas to show board and scores and bind click listener
def init_board():
    global board, playerCountIntVar, computerCountIntVar, gameMessage
    global gameCanvas , gameCanvasWindow
    board = [ [None]*8  for n in range(8)] # list comprehension
    gameCanvasWindow = Tk()
    gameCanvasWindow.title("Reversi")
    
    gameCanvasWindow.geometry("500x600")
    gameCanvas = Canvas(gameCanvasWindow, width=500, height=500)
    gameCanvas.grid(row=1,column=1,columnspan=2)
    
#     set score variables    
    playerCountIntVar = IntVar(0)
    computerCountIntVar = IntVar(0)
    
    playerScoreTitleLabel = Label(gameCanvasWindow,text="Player: ",font= Font(family = 'Time',size = 16))
    playerScoreTitleLabel.grid(row=3,column=1)    
    playerScoreLabel = Label(gameCanvasWindow, textvariable=playerCountIntVar,font= Font(family = 'Time',size = 16))
    playerScoreLabel.grid(row=3,column=2)
    computerScoreTitleLabel = Label(gameCanvasWindow,text="Computer: ",font= Font(family = 'Time',size = 16))
    computerScoreTitleLabel.grid(row=4,column=1)
    computerScoreLabel = Label(gameCanvasWindow, textvariable=computerCountIntVar,font= Font(family = 'Time',size = 16))
    computerScoreLabel.grid(row=4,column=2)
    gameMessage = StringVar()
    gameMessageLabel = Label(gameCanvasWindow, textvariable=gameMessage, fg ="red" ,font= Font(family = 'Time',size = 16))
    gameMessageLabel.grid(row=2,column=1)
    
    restartGame = Button(master=gameCanvasWindow, text='Reset Game',bg="orange", command=lambda:resetGame(), font = Font(family='Helvetica', size=14))
    restartGame.grid(row=2,column=2)

    gameCanvas.bind("<Button-1>", mouseClickListener)
    if not userTurn:
        gameCanvas.after(200, playGame)
    pass

# draw board for the game in canvas
def drawReversiBoard():
    global board
    global gameCanvas
    global widthOfBox
    global boxesBoard
    x,y = 0,0 # starting position

    for row in range(len(board)):
        boxesBoard.append([])
        for col in range(len(board[row])):
            boxesBoard[row].append(gameCanvas.create_rectangle(x, y, widthOfBox+x, widthOfBox+y, fill='green'))
            x = x + widthOfBox  # move right
        y = y + widthOfBox # move down
        x = 0 # rest to left edge
    
#     set first four piece for start

    borderBox1p = gameCanvas.coords(boxesBoard[3][3])
    borderBox2c = gameCanvas.coords(boxesBoard[3][4])
    borderBox3c = gameCanvas.coords(boxesBoard[4][3])
    borderBox4p = gameCanvas.coords(boxesBoard[4][4])
    
#     update in board array
    board[3][3] = playerClr
    board[3][4] = computerClr
    board[4][3] = computerClr
    board[4][4] = playerClr
    
    gameCanvas.create_oval(borderBox1p[0]+2, borderBox1p[1]+2, borderBox1p[2]-2,borderBox1p[3]-2, fill=playerClr, outline="")
    gameCanvas.create_oval(borderBox2c[0]+2, borderBox2c[1]+2, borderBox2c[2]-2,borderBox2c[3]-2, fill=computerClr, outline="")
    gameCanvas.create_oval(borderBox3c[0]+2, borderBox3c[1]+2, borderBox3c[2]-2,borderBox3c[3]-2, fill=computerClr, outline="")
    gameCanvas.create_oval(borderBox4p[0]+2, borderBox4p[1]+2, borderBox4p[2]-2,borderBox4p[3]-2, fill=playerClr, outline="")
    
#     update score of first 4 moves
    updateScore()
    
    pass

# select turn from user
def selectTurn(turn, LastWindow):
    global userTurn, realUserTurn
    realUserTurn = userTurn = turn
    LastWindow.destroy()
    init_board()
    drawReversiBoard()
    
    pass


def latestIndicator(x1,y1,x2,y2):
    global indicator
    if indicator != None:
        gameCanvas.delete(indicator)
    indicator = gameCanvas.create_rectangle(x1+35,y1+35,x2-35,y2-35, fill="#FF0000", outline="")


# select turn window to select who plays first move
def selectTurnScreen():
    turnWindow = Tk()
    turnWindow.title("Reversi")
    turnWindow.option_add("*Button.Background", "black")
    turnWindow.option_add("*Button.Foreground", "white")
    
    #You can set the geometry attribute to change the root windows size
    turnWindow.geometry("500x500") #You want the size of the app to be 500x500
    turnWindow.resizable(0, 0) #Don't allow resizing in the x or y direction
    
    back = Frame(master=turnWindow,bg='black')
    back.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
    back.pack(fill=BOTH, expand=1) #Expand the frame to fill the root window
    
    
    info = Label(master=back, text='Who will go first?', bg='black', fg='white',font= Font(family = 'Time',size = 32))
    info.pack()
    playerFirst = Button(master=back, text='Player',bg="green", command=lambda:selectTurn(True, turnWindow), font = Font(family='Helvetica', size=36))
    playerFirst.pack(pady=10)
    compFirst = Button(master=back, text='Computer',bg="orange", command=lambda:selectTurn(False,turnWindow),  font = Font(family='Helvetica', size=36))
    compFirst.pack()
   
    turnWindow.mainloop()
    pass

# select difficulty level from user
def selectMode(mode, LastWindow):
    global difficultyLevel
    LastWindow.destroy()
    difficultyLevel = mode
    selectTurnScreen()
    pass

# select difficulty level window to get difficulty
def startUpScreen():
    startUp = Tk()
    startUp.title("Reversi")
    startUp.option_add("*Button.Background", "black")
    startUp.option_add("*Button.Foreground", "white")
    
    startUp.geometry("500x500") #size of the window to be 500x500
    startUp.resizable(0, 0) #Don't allow resizing in the x or y direction
    
    back = Frame(master=startUp,bg='black')
    back.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
    back.pack(fill=BOTH, expand=1) #Expand the frame to fill the root window
    
    
    info = Label(master=back, text='Reversi', bg='black', fg='white',font= Font(family = 'Time',size = 40))
    info.pack(fill=X)
    easy = Button(master=back, text='Easy' ,bg="green", command=lambda:selectMode(0,startUp), font = Font(family='Helvetica', size=36))
    easy.pack(side="left")
    hard = Button(master=back, text='Hard', bg="orange" ,command=lambda:selectMode(1,startUp), font = Font(family='Helvetica', size=36))
    hard.pack(side="left")
    close = Button(master=back, text='Quit', bg="red", command=startUp.destroy, font = Font(family='Helvetica', size=36))
    close.pack(expand=True,fill=X)
   
    startUp.mainloop()
    pass


# start the game from startup window to select difficulty
startUpScreen()
