import pygame
from pygame.locals import *
from square import *
from ship import *
from board import *
from button import *
from copy import deepcopy
pygame.init()

#params that stay constant
gameOn = True
numships = 5
ships = [5,4,3,3,2]
boardwidth = 10
boardheight = 10
screenwidth = 800
screenheight = 600
squarewidth = 25
squareheight = 25
separation = 3
screen = pygame.display.set_mode((screenwidth,screenheight))
font = pygame.font.SysFont("Ubuntu",30)
pygame.display.set_caption("Battleship")
ship5im = pygame.image.load("images/ship5.png").convert_alpha()
ship4im = pygame.image.load("images/ship4.png").convert_alpha()
ship3im1 = pygame.image.load("images/ship3_1.png").convert_alpha()
ship3im2 = pygame.image.load("images/ship3_2.png").convert_alpha()
ship2 = pygame.image.load("images/ship2.png").convert_alpha()
shipims = [ship5im,ship4im,ship3im1,ship3im2,ship2]

#rescale ship images
for i,im in enumerate(shipims):
    size = ships[i]
    im = pygame.transform.scale(im,(squarewidth,size*squareheight+size-1*separation))
    shipims[i] = pygame.transform.rotate(im,90)
#need to be reset with new game
playerturn = 0 #0 - p1, 1 - p2
hoverloc = (-1,-1)
countdown = 5
timeleft = deepcopy(countdown)
clicked = False
shipids = [0,1,2,3,4]
curship = 0 #index of ship
orientation = 0 #0 - right, 1 - down, 2 - left, 3 - up
field = [] #highlighted ship area
prevfield = [] #previous highlighted ship area
setupdone = False
gamestate = -1
p1board = Board(boardwidth,
        boardheight,
        screenwidth,
        screenheight,
        shipims,
        squarewidth=squarewidth,
        squareheight=squareheight,
        separation=separation,
        numships=numships)
p2board = Board(boardwidth,
        boardheight,
        screenwidth,
        screenheight,
        shipims,
        squarewidth=squarewidth,
        squareheight=squareheight,
        separation=separation,
        numships=numships)
boards = [p1board,p2board]
buttons = []
imstoblit = []
curshiptoblit = None

#Game loop
while gameOn:
    for event in pygame.event.get():
        #Game setup
        if not setupdone and gamestate == -1: 
            #p1 sets up p2's board, p2 sets up p1's board
            board = boards[(playerturn+1)%2]
            displaytext = "Player "+str(playerturn+1)+" setup"
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                    gameOn = False
                if event.key == K_UP:
                    board.buttons[shipids[curship]].clicked = False
                    curship = (curship-1)%len(shipids)
                    board.buttons[shipids[curship]].clicked = True
                if event.key == K_DOWN:
                    board.buttons[shipids[curship]].clicked = False
                    curship = (curship+1)%len(shipids)
                    board.buttons[shipids[curship]].clicked = True
                if event.key == K_RIGHT:
                    orientation = (orientation+1)%4
                    for i,im in enumerate(shipims):
                        shipims[i] = pygame.transform.rotate(im,90)
                if event.key == K_LEFT:
                    orientation = (orientation-1)%4
                    for i,im in enumerate(shipims):
                        shipims[i] = pygame.transform.rotate(im,-90)

            elif event.type == MOUSEMOTION:
                mousepos = event.pos
                if board.isonboard(event.pos):
                    hoverloc = board.getsquare(event.pos)
    
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: #left click
                    clicked = True
                elif event.button == 3: #right click
                    orientation = (orientation+1)%4
                    for i,im in enumerate(shipims):
                        shipims[i] = pygame.transform.rotate(im,90)

            elif event.type == QUIT:
                gameOn = False

            board.resetcolour(prevfield)
            prevfield = field
            curships = [ships[shipid] for shipid in shipids]
            field = board.makefield(curships[curship],hoverloc,orientation)
            if board.isfieldonboard(field):
                shipim = shipims[shipids[curship]]
                shippos = board.topleftposoffield(field,orientation)
                curshiptoblit = (shipim,shippos)

            if clicked:
                if board.isonboard(mousepos):
                    if board.placeship(shipids[curship],field):
                        shipid = shipids.pop(curship)
                        shipim = shipims[shipid]
                        shippos = board.topleftposoffield(field,orientation)
                        imstoblit.append((shipim,shippos))
                        board.buttons[shipid].buttoncolour = (150,150,170)
                        board.buttons[shipid].clicked = False
                        curshiptoblit = None
                        if not shipids: #if all ships placed
                            #gamestate = 0 #player transition
                            shipids = [0,1,2,3,4]
                            if playerturn != 0:
                                setupdone = True
                            playerturn = (playerturn+1)%2
                            imstoblit = []
                        else:
                            curship = 0
                            board.buttons[shipids[curship]].clicked = True
                else:
                    board.hovership(field)
                    for button in board.buttons:
                        if button.ison(mousepos):
                            shipid = button.buttonid
                            if shipid in shipids:
                                board.buttons[shipids[curship]].clicked = False
                                curship = shipids.index(shipid) 
                                button.clicked = True
            else:
                board.hovership(field)
            clicked = False
     
        else: 
            if gamestate == 0: #player transition
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                        gameOn = False
                elif event.type == QUIT:
                    gameOn = False
                print("IN PLAYER TRANSITION")
                pygame.time.wait(5)
                playerturn = (playerturn+1)%2

            elif gamestate > 0: #game over, replay or quit
                displaytext = "Player "+str(gamestate)+" wins!" 
            
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                        gameOn = False

                elif event.type == MOUSEMOTION:
                    mousepos = event.pos
                    if board.isonboard(pos):
                        hoverloc = board.getsquare(pos)
    
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1: #left click
                        clicked = True

                elif event.type == QUIT:
                    gameOn = False
            
                if len(buttons) == 0:
                    buttons.append(Button(len(buttons),font,screenwidth//2-180,screenheight//2-30,180,60,text = "Play again"))
                    buttons.append(Button(len(buttons),font,screenwidth//2,screenheight//2-30,180,60,text = "Quit"))

                if clicked:
                    option = -1
                    for button in buttons:
                        if button.ison(mousepos):
                            if button.text == "Play again":
                                option = 0
                            elif button.text == "Quit":
                                option = 1
                                
                    if option == 0: 
                        #reset game
                        boards[0].reset()
                        boards[1].reset()
                        buttons = []
                        playerturn = 0 
                        hoverloc = (-1,-1)
                        ships = deepcopy(defaultships)
                        curship = 0 
                        orientation = 0
                        field = []
                        prevfield = [] 
                        setupdone = False
                        gamestate = -1
                        buttons = []
                    elif option == 1:
                        #quit
                        gameOn = False
                clicked = False

            else: #if setup is done and game isn't over, we can begin the game
                board = boards[playerturn]
                displaytext = "Player "+str(playerturn+1)+" turn:"
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE or event.key == K_ESCAPE:
                        gameOn = False

                elif event.type == MOUSEMOTION:
                    mousepos = event.pos
                    if board.isonboard(mousepos):
                        hoverloc = board.getsquare(mousepos)
    
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1: #left click
                        clicked = True
    
                elif event.type == QUIT:
                    gameOn = False
            
                board.resetcolour(prevfield)
                prevfield = [hoverloc]
    
                if clicked:
                    if board.isfieldonboard([hoverloc]):
                        shipsleft = board.attack(hoverloc)
                        if shipsleft > 0:
                            displaytext+= " HIT!"
                            gamestate = 0

                        elif shipsleft == 0: #game over
                            gamestate = playerturn+1

                        elif shipsleft == -1:#if they attack where a sunk ship is - do nothing
                            board.hovership([hoverloc])

                        else: #it's a miss
                            displaytext += " miss :("
                            gamestate = 0

                else:
                    board.hovership([hoverloc])
            
                clicked = False
            
    board.render(screen,displaytext,font,mousepos)
    for button in buttons:
        button.render(screen,mousepos)
    for im,pos in imstoblit:
        screen.blit(im,pos)
    if curshiptoblit is not None:
        im,pos = curshiptoblit
        screen.blit(im,pos)
    pygame.display.flip()

















