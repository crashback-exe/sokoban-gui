from sys import exit
from subprocess import check_output
from dataclasses import dataclass
from enum import Enum
from tkinter import *


@dataclass
class Coords2D:
    x: float
    y: float


width = 10
height = 10
goalsCount = 3

PATH_COLOR = 'white'
WALL_COLOR = 'grey'
PLAYER_COLOR = 'red'
BOX_COLOR = '#C08457'
TARGET_COLOR = '#00BB2D'

WALL = '#'
PATH = ' '
level = [[] for _ in range(height)]
boxesPos = []
targetsPos = []
playerMovements = []
boxesMovements = [[] for _ in range(goalsCount)]

MARGIN = Coords2D(10, 10)
DIMLEVEL = Coords2D(600, 600)
DIMWINDOW = Coords2D(MARGIN.x * 2 + DIMLEVEL.x, MARGIN.y * 2 + DIMLEVEL.y)
dimCell = Coords2D(DIMLEVEL.x / width, DIMLEVEL.y / height)

root = Tk()
root.title("Sokoban")
root.resizable(0, 0)
canvas = Canvas(root, width=DIMWINDOW.x, height=DIMWINDOW.y, bg="#220901")
canvas.pack()


class DIRECTIONS(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


STEPS = {
    DIRECTIONS.UP: Coords2D(0, -1),
    DIRECTIONS.DOWN: Coords2D(0, 1),
    DIRECTIONS.LEFT: Coords2D(-1, 0),
    DIRECTIONS.RIGHT: Coords2D(1, 0)
}


def RecvData():
    global playerPos
    global boxesPos
    global targetsPos
    temp = ''

    data = check_output([str('bin\\Sokoban.exe'), str(width), str(height), str(goalsCount), 'data'], shell=True).decode("utf-8")

    i = 0
    j = 0
    while data[i] != '-':
        if i / width == i // width and i > 0:
            j += 1
        level[j].append(data[i])
        i += 1

    i += 1
    while data[i] != '-':
        temp = temp + data[i]
        i += 1
    playerPos = eval(temp)

    i += 1
    temp = ''
    while data[i] != '-':
        temp = temp + data[i]
        i += 1
    boxesPos = eval(temp)

    i += 1
    temp = ''
    while data[i] != '-':
        temp = temp + data[i]
        i += 1
    targetsPos = eval(temp)


def CellOccupied(cell, objects):
    for object in objects:
        if cell.x == object.x and cell.y == object.y:
            return True
    return False


def PrintPlayer(playerPos):
    x = MARGIN.x + playerPos.x * dimCell.x + dimCell.x / 2
    y = MARGIN.x + playerPos.y * dimCell.y + dimCell.y / 2
    canvas.create_polygon([x - 20, y + 20, x + 20, y + 20, x + 20, y, x, y, x + 10, y, x + 10, y - 10, x - 10, y - 10, x - 10, y, x, y, x - 20, y], fill=PLAYER_COLOR, outline='black')


def PrintTarget(targetPos):
    r = 8
    x = MARGIN.x + targetPos.x * dimCell.x + dimCell.x / 2
    y = MARGIN.x + targetPos.y * dimCell.y + dimCell.y / 2
    canvas.create_oval(x-r, y-r, x+r, y+r, fill=TARGET_COLOR, outline='black')


def PrintCell(boxPos, color):
    x = MARGIN.x + boxPos.x * dimCell.x
    y = MARGIN.x + boxPos.y * dimCell.y
    canvas.create_rectangle(x, y, x + dimCell.x, y + dimCell.y, fill=color, outline='black')


def ClearCell(cell):
    PrintCell(cell, PATH_COLOR)
    if CellOccupied(cell, targetsPos):
        PrintTarget(cell)


def PrintLevel():
    y0 = MARGIN.y
    for i in range(width):
        x0 = MARGIN.x
        x1 = x0 + dimCell.x
        y1 = y0 + dimCell.y

        for j in range(height):
            if (level[i][j] == WALL):
                color = WALL_COLOR

            else:
                color = PATH_COLOR

            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='black')

            x0 = x1
            x1 = x0 + dimCell.x

        y0 = y1

    for i in range(goalsCount):
        PrintCell(boxesPos[i], BOX_COLOR)
        PrintTarget(targetsPos[i])

    PrintPlayer(playerPos)


def PlayerMove(direction):
    to = Coords2D(playerPos.x + STEPS[direction].x,
                  playerPos.y + STEPS[direction].y)

    if to.x < 0 or to.x >= width or to.y < 0 or to.y >= height or level[to.y][to.x] == WALL:
        return

    for boxPos in boxesPos:
        if to.x != boxPos.x or to.y != boxPos.y:
            continue

        boxTo = Coords2D(to.x + STEPS[direction].x, to.y + STEPS[direction].y)
        if ((boxTo.x < width and boxTo.y < height and boxTo.x >= 0 and boxTo.y >= 0)
                and level[boxTo.y][boxTo.x] != WALL and not CellOccupied(boxTo, boxesPos)):

            for i in range(goalsCount):
                boxesMovements[i].append(
                    Coords2D(boxesPos[i].x, boxesPos[i].y))
            ClearCell(boxPos)
            boxPos.x = boxTo.x
            boxPos.y = boxTo.y
            PrintCell(boxPos, BOX_COLOR)

            playerMovements.append(Coords2D(playerPos.x, playerPos.y))
            ClearCell(playerPos)
            playerPos.x = to.x
            playerPos.y = to.y
            PrintPlayer(playerPos)
            return
        return

    for i in range(goalsCount):
        boxesMovements[i].append(Coords2D(boxesPos[i].x, boxesPos[i].y))

    playerMovements.append(Coords2D(playerPos.x, playerPos.y))
    ClearCell(playerPos)
    playerPos.x = to.x
    playerPos.y = to.y
    PrintPlayer(playerPos)


def CloseWindow():
    root.destroy()
    exit()


def KeyPress(event):
    global playerPos

    win = True
    for i in range(goalsCount):
        if not CellOccupied(boxesPos[i], targetsPos):
            win = False
            break

    if event.char == 'w' and not win:
        PlayerMove(DIRECTIONS.UP)

    elif event.char == 'a' and not win:
        PlayerMove(DIRECTIONS.LEFT)

    elif event.char == 's' and not win:
        PlayerMove(DIRECTIONS.DOWN)

    elif event.char == 'd' and not win:
        PlayerMove(DIRECTIONS.RIGHT)

    elif event.char == 'q' and not win:
        if len(playerMovements) > 0:
            ClearCell(playerPos)
            playerPos.x = playerMovements[len(playerMovements) - 1].x
            playerPos.y = playerMovements[len(playerMovements) - 1].y
            playerMovements.pop()
            PrintPlayer(playerPos)

        for i in range(goalsCount):
            if len(boxesMovements[i]) > 0:
                ClearCell(boxesPos[i])
                boxesPos[i].x = boxesMovements[i][len(boxesMovements[i]) - 1].x
                boxesPos[i].y = boxesMovements[i][len(boxesMovements[i]) - 1].y
                boxesMovements[i].pop()
                PrintCell(boxesPos[i], BOX_COLOR)
        return

    elif event.char == 'r':
        for i in range(height):
            level[i].clear()
        boxesPos.clear()
        targetsPos.clear()
        playerMovements.clear()
        for i in range(goalsCount):
            boxesMovements[i].clear()
        canvas.delete("all")
        main()

    elif event.keysym == 'Escape':
        CloseWindow()

    win = True
    for i in range(goalsCount):
        if not CellOccupied(boxesPos[i], targetsPos):
            win = False
            break

    if win:
        canvas.create_text(MARGIN.x + DIMLEVEL.x/2, MARGIN.y + DIMLEVEL.y/2,
                           text='Level COMPLETED!', anchor=CENTER, font=("Garamond", 50), fill="black")
        canvas.create_text(MARGIN.x + DIMLEVEL.x/2, MARGIN.y + DIMLEVEL.y/2 + 40,
                           text='press R to restart', anchor=CENTER, font=("Garamond", 20), fill="black")


def main():
    RecvData()
    PrintLevel()

    root.bind("<KeyPress>", KeyPress)
    root.protocol("WM_DELETE_WINDOW", CloseWindow)
    root.mainloop()


if __name__ == "__main__":
    main()
