from tkinter import *

import subprocess
import json

# Sokoban executable path
path = "bin\\Sokoban.exe"

# Config
height = 8
width = 8
boxCount = 3


def generate_level() -> dict:

	# Get output and fix backspace characters
	output = list(subprocess.check_output([path, str(height), str(
		width), str(boxCount), "json"], shell=True).decode("utf-8"))

	for i in range(len(output)):
		if output[i] == "\b":
			output[i-1] = ""
			output[i] == ""

	# Convert to json
	output = "".join(output).replace("\b", "")
	output = json.loads(output)

	global level, player, boxes, targets
	level = output["level"]
	player = output["player"]
	boxes = output["box"]
	targets = output["target"]

	return output


output = generate_level()

# Create the main window
window = Tk()
window.title("Sokoban")
window.resizable(False, False)


CELL_SIZE = 75

# Create a canvas to draw the grid on
canvas = Canvas(window, width=CELL_SIZE * width, height=CELL_SIZE * height)
canvas.pack()

BOX_COLOR = "red"
TARGET_COLOR = "lime"
PLAYER_COLOR = "blue"
WALL_COLOR = "gray"
SPACE_COLOR = "white"

OUTLINE_COLOR = "white"


win_state = False

def move(x_increment: int, y_increment: int) -> None:
	y = player["y"] + y_increment
	x = player["x"] + x_increment
	if y >= height or x >= width or level[y][x] == "#":
		return
	# the player wants to go in a box
	elif [x, y] in boxes:
		# if the cell next to the box is empty
		if y + y_increment < height and x + x_increment < width and level[y + y_increment][x + x_increment] == " " and [x + x_increment, y + y_increment] not in boxes:
			# move the box
			boxes[boxes.index([x, y])] = [boxes[boxes.index(
				[x, y])][0] + x_increment, boxes[boxes.index([x, y])][1] + y_increment]

			# repaint freed cell
			repaint_free_cell(player["x"], player["y"])

			# move player
			player["x"] = x
			player["y"] = y

			# repaint box
			paint_box(boxes.index([x + x_increment, y + y_increment]))
	else:
		repaint_free_cell(player["x"], player["y"])
		player["x"] = x
		player["y"] = y


# Config key events
def on_press(event):
	key = event.char
	global win_state
	if key == "r" or win_state:
		win_state = False
		global output

		output = generate_level()
		paint_window()
		paint_boxes()
	elif key == "w":
		move(0, -1)
	elif key == "a":
		move(-1, 0)
	elif key == "s":
		move(0, 1)
	elif key == "d":
		move(1, 0)
	paint_player()
	check_win()


def check_win() -> None:
	for box in boxes:
		if box not in targets:
			return
	canvas.create_text((CELL_SIZE * width / 2, CELL_SIZE * height / 2), text='You Won!', anchor=CENTER, font=("Arial", 32), fill="black")
	canvas.create_text((CELL_SIZE * width / 2, CELL_SIZE * height / 2 + 40), text='Press any key to continue', anchor=CENTER, font=("Arial", 24), fill="black")
	global win_state
	win_state = True

def paint_window() -> None:
	# Draw the rectangles for each cell in the grid
	for x in range(len(level[0])):
		for y in range(len(level)):
			x1: int = x * CELL_SIZE
			y1: int = y * CELL_SIZE
			x2: int = x1 + CELL_SIZE
			y2: int = y1 + CELL_SIZE
			color: str

			# wall
			if level[y][x] == "#":
				color = WALL_COLOR

			# space
			if level[y][x] == " ":
				color = SPACE_COLOR

			# target
			for target in targets:
				if x == target[0] and y == target[1]:
					color = TARGET_COLOR
					break

			canvas.create_rectangle(
				x1, y1, x2, y2,
				fill=color,
				outline=OUTLINE_COLOR
			)


def repaint_free_cell(x: int, y: int) -> None:
	x1: int = x * CELL_SIZE
	y1: int = y * CELL_SIZE
	x2: int = x1 + CELL_SIZE
	y2: int = y1 + CELL_SIZE

	color: str
	if [x, y] in targets:
		color = TARGET_COLOR
	else:
		color = SPACE_COLOR
	canvas.create_rectangle(
		x1, y1, x2, y2,
		fill=color,
		outline=OUTLINE_COLOR
	)


def paint_player() -> None:
	x1: int = player["x"] * CELL_SIZE
	y1: int = player["y"] * CELL_SIZE
	x2: int = x1 + CELL_SIZE
	y2: int = y1 + CELL_SIZE

	canvas.create_rectangle(
		x1, y1, x2, y2,
		fill=PLAYER_COLOR,
		outline=OUTLINE_COLOR
	)


def paint_box(box: int) -> None:
	x1: int = boxes[box][0] * CELL_SIZE
	y1: int = boxes[box][1] * CELL_SIZE
	x2: int = x1 + CELL_SIZE
	y2: int = y1 + CELL_SIZE
	canvas.create_rectangle(
		x1, y1, x2, y2,
		fill=BOX_COLOR,
		outline=OUTLINE_COLOR
	)


def paint_boxes() -> None:
	for box in range(len(boxes)):
		paint_box(box)


paint_window()
paint_player()
paint_boxes()

# add the event
window.bind('<KeyPress>', on_press)

# Run the tkinter event loop
window.mainloop()
