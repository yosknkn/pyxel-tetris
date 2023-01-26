import pyxel, random
import numpy as np

minos = {
    0: np.array(
        [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0],
        ]
    ),
    1: np.array(
        [
            [0, 2, 2],
            [2, 2, 0],
            [0, 0, 0],
        ]
    ),
    2: np.array(
        [
            [3, 3, 0],
            [0, 3, 3],
            [0, 0, 0],
        ]
    ),
    3: np.array(
        [
            [0, 0, 4],
            [4, 4, 4],
            [0, 0, 0],
        ]
    ),
    4: np.array(
        [
            [5, 0, 0],
            [5, 5, 5],
            [0, 0, 0],
        ]
    ),
    5: np.array(
        [
            [0, 0, 0, 0],
            [6, 6, 6, 6],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
    ),
    6: np.array(
        [
            [7, 7],
            [7, 7],
        ]
    ),
}


class App:
    def __init__(self) -> None:
        self.gameover = False
        pyxel.init(150, 200)
        pyxel.load("my_resource.pyxres")
        self.field = Field(x_offset=16, y_offset=8, block_size=8)
        self.nexts_field = NextField(x_offset=120, y_offset=16, block_size=4)
        self.hold_field = HoldField(x_offset=8, y_offset=16, block_size=4)
        self.action_viewer=ActionViewer(70,100)
        self.gravity = 15
        self.falling_mino = None
        self.nexts = []
        self.add_nexts()
        self.hold = None
        self.holded = False
        self.lines = 0
        self.points=0
        self.push_frame = {}
        self.pause=False
        self.normal=False
        pyxel.run(self.update, self.draw)

    def push(self, button):
        if pyxel.btn(button):
            if button not in self.push_frame:
                self.push_frame[button] = pyxel.frame_count
                return True
            else:
                if pyxel.frame_count - self.push_frame[button] >= 10:
                    return (
                        True
                        if (pyxel.frame_count - self.push_frame[button]) % 2 == 0
                        else False
                    )
                else:
                    return False
        else:
            if button in self.push_frame:
                self.push_frame.pop(button)
            return False

    def update(self):
        if self.gameover == True:
            return
        
        if self.push(pyxel.KEY_R):
            if self.pause:
                self.pause=False
            else:
                self.pause=True

        if self.push(pyxel.KEY_H):
            self.gravity-=1
        
        if self.push(pyxel.KEY_F):
            if self.normal:
                self.normal=False
            else:
                self.normal=True
        
        if self.pause:
            return

        if self.falling_mino == None:
            self.falling_mino = FallingMino(self.nexts[0], self.gravity, self.field,False if self.normal else (pyxel.rndi(0,9)<1))
            self.nexts.pop(0)
            self.add_nexts()

        if self.push(pyxel.KEY_D):
            if self.falling_mino.is_opposit==True:
                self.falling_mino.move(-1)
            else:
                self.falling_mino.move(1)
        if self.push(pyxel.KEY_A):
            if self.falling_mino.is_opposit==True:
                self.falling_mino.move(1)
            else:
                self.falling_mino.move(-1)

        if pyxel.btn(pyxel.KEY_S):
            self.falling_mino.soft_drop = True
        else:
            self.falling_mino.soft_drop = False
        if self.push(pyxel.KEY_W):
            self.falling_mino.hard_drop()
            self.field.set_mino(
                self.falling_mino.x, self.falling_mino.y, self.falling_mino.minoshape
            )
            self.holded = False
            self.falling_mino = None

        if pyxel.btnp(pyxel.KEY_LEFT):
            if self.falling_mino!=None:
                self.falling_mino.rotate(1)
        if pyxel.btnp(pyxel.KEY_RIGHT):
            if self.falling_mino!=None:
                self.falling_mino.rotate(-1)

        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.holded == False:
                if self.hold == None:
                    self.hold = self.falling_mino.mino
                    self.falling_mino = None
                else:
                    h = self.hold
                    self.hold = self.falling_mino.mino
                    self.falling_mino = FallingMino(h, self.gravity, self.field,False if self.normal else (pyxel.rndi(0,9)<1))
                self.holded = True

        line=self.field.check()
        self.action_viewer.set_action(line)
        self.lines += line
        
        match line:
            case 1:
                self.points+=100
            case 2:
                self.points+=300
            case 3:
                self.points+=500
            case 4:
                self.points+=800
            case _:
                pass

        if self.lines - (31 - self.gravity) * 5 > 0:
            self.gravity -= 1

        if self.falling_mino != None:
            if self.falling_mino.update():
                self.field.set_mino(
                    self.falling_mino.x,
                    self.falling_mino.y,
                    self.falling_mino.minoshape,
                )
                self.holded = False
                self.falling_mino = None

        if self.field.gameover_check():
            self.gameover = True

    def draw(self):
        if self.gameover == True:
            pyxel.text(70, 100, "Game Over", 0)
            return
        if self.pause == True:
            pyxel.text(70, 100, "pause", 0)
            return
        pyxel.cls(13)
        self.field.draw()
        self.nexts_field.draw(self.nexts)
        self.hold_field.draw(self.hold)
        if self.falling_mino != None:
            self.falling_mino.draw()

        pyxel.bltm(0, 0, 0, 0, 0, 150, 200, 14)
        pyxel.text(0, 0, f"lines: {self.lines}", 0)
        pyxel.text(0, 5, f"point: {self.points}", 0)
        if self.normal : pyxel.text(0,180,"Normal mode",0)
        self.action_viewer.draw()

    def add_nexts(self):
        while len(self.nexts) < 10:
            minos = [0, 1, 2, 3, 4, 5, 6]
            random.shuffle(minos)
            for x in minos:
                self.nexts.append(x)


class FallingMino:
    def __init__(self, mino, gravity, field,is_opposit) -> None:
        self.mino = mino
        self.minoshape = minos[mino]
        self.x = 7 if mino == 6 else 6
        self.y = 2
        self.block_size = field.block_size
        self.falled_frame = pyxel.frame_count
        self.gravity = gravity
        self.field = field
        self.soft_drop = False
        self.rot = 0
        self.collided = 0
        self.move_count = 0
        self.is_opposit=is_opposit

    def update(self):
        if (pyxel.frame_count - self.falled_frame >= self.gravity) or (
            self.soft_drop
            and (pyxel.frame_count - self.falled_frame) * 20 >= self.gravity
        ):
            if self.collision(self.x, self.y + 1):
                if self.collided != 0:
                    if pyxel.frame_count - self.collided > 15 or self.move_count >= 15:
                        self.collided = 0
                        return True
                else:
                    self.collided = pyxel.frame_count
                    self.move_count = 0
            else:
                self.y += 1
            self.falled_frame = pyxel.frame_count
            return False

    def collision(self, x, y):
        for v in range(self.minoshape.shape[1]):
            for u in range(self.minoshape.shape[0]):
                if self.field.blocks[u + y][v + x] != 13 and self.minoshape[u][v] != 0:
                    return True
        return False

    def draw(self):
        ghost_y = self.y
        while not self.collision(self.x, ghost_y + 1):
            ghost_y += 1
        for y in range(self.minoshape.shape[1]):
            for x in range(self.minoshape.shape[0]):
                color = self.minoshape[y][x]
                if color != 0:
                    pyxel.blt(
                        self.field.x_offset
                        + self.block_size * self.x
                        + self.block_size * x,
                        self.field.y_offset
                        + self.block_size * (ghost_y - 3)
                        + self.block_size * y,
                        0,
                        8 * 7,
                        0,
                        8,
                        8,
                    )
        for y in range(self.minoshape.shape[1]):
            for x in range(self.minoshape.shape[0]):
                color = self.minoshape[y][x]
                if color != 0:
                    pyxel.blt(
                        self.field.x_offset
                        + self.block_size * self.x
                        + self.block_size * x,
                        self.field.y_offset
                        + self.block_size * (self.y - 3)
                        + self.block_size * y,
                        0,
                        8 * self.mino,
                        8 if self.is_opposit else 0,
                        8,
                        8,
                    )

    def move(self, direction):
        if not self.collision(self.x + direction, self.y):
            self.x += direction
        if self.collided != 0:
            self.move_count += 1
            self.collided = pyxel.frame_count

    def hard_drop(self):
        while not self.collision(self.x, self.y + 1):
            self.y += 1

    def rotate(self, rotate):
        self.minoshape = np.rot90(self.minoshape, rotate)
        self.rot += rotate
        self.rot %= 4
        if self.collided != 0:
            self.move_count += 1
            self.collided = pyxel.frame_count
        if not self.collision(self.x, self.y):
            return
        dx, dy = 0, 0
        #回転補正SRS
        # iミノ補正
        if self.mino == 5:
            # 1
            if self.rot == 3 and rotate == -1:
                dx = -2
            if self.rot == 0 and rotate == 1:
                dx = 2
            if self.rot == 2 and rotate == -1:
                dx = -1
            if self.rot == 3 and rotate == 1:
                dx = 1
            if self.rot == 1 and rotate == -1:
                dx = 2
            if self.rot == 2 and rotate == 1:
                dx = -2
            if self.rot == 0 and rotate == -1:
                dx = 1
            if self.rot == 1 and rotate == 1:
                dx = -1
            if not self.collision(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
                return
            # 2
            if self.rot == 3 and rotate == -1:
                dx = 1
            if self.rot == 0 and rotate == 1:
                dx = -1
            if self.rot == 2 and rotate == -1:
                dx = 2
            if self.rot == 3 and rotate == 1:
                dx = -2
            if self.rot == 1 and rotate == -1:
                dx = -1
            if self.rot == 2 and rotate == 1:
                dx = 1
            if self.rot == 0 and rotate == -1:
                dx = -2
            if self.rot == 1 and rotate == 1:
                dx = -2
            if not self.collision(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
                return
            # 3
            if self.rot == 3 and rotate == -1:
                dx = -2
                dy = 1
            if self.rot == 0 and rotate == 1:
                dx = 2
                dy = -1
            if self.rot == 2 and rotate == -1:
                dx = -1
                dy = -2
            if self.rot == 3 and rotate == 1:
                dx = 1
                dy = 2
            if self.rot == 1 and rotate == -1:
                dx = 2
                dy = -1
            if self.rot == 2 and rotate == 1:
                dx = -2
                dy = 1
            if self.rot == 0 and rotate == -1:
                dx = 1
                dy = 2
            if self.rot == 1 and rotate == 1:
                dx = -1
                dy = -2
            if not self.collision(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
                return
            # 4
            if self.rot == 3 and rotate == -1:
                dx = 1
                dy = -2
            if self.rot == 0 and rotate == 1:
                dx = -1
                dy = 2
            if self.rot == 2 and rotate == -1:
                dx = 2
                dy = 1
            if self.rot == 3 and rotate == 1:
                dx = -2
                dy = -1
            if self.rot == 1 and rotate == -1:
                dx = -1
                dy = 2
            if self.rot == 2 and rotate == 1:
                dx = 1
                dy = -2
            if self.rot == 0 and rotate == -1:
                dx = -2
                dy = -1
            if self.rot == 1 and rotate == 1:
                dx = -2
                dy = 1
            if not self.collision(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
                return

        # それ以外1
        if (
            self.rot == 3
            or (self.rot == 0 and rotate == -1)
            or (self.rot == 2 and rotate == 1)
        ):
            dx = -1
        else:
            dx = 1
        if not self.collision(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return
        # 2
        if self.rot == 1 or self.rot == 3:
            dy = -1
        else:
            dy = 1
        if not self.collision(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return
        # 3
        dx, dy = 0, 0
        if self.rot == 1 or self.rot == 3:
            dy = 2
        else:
            dy = -2
        if not self.collision(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return
        # 4
        if (
            self.rot == 3
            or (self.rot == 0 and rotate == -1)
            or (self.rot == 2 and rotate == 1)
        ):
            dx = -1
        else:
            dx = 1
        if not self.collision(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return


class Field:
    def __init__(self, *, x_offset=0, y_offset=0, block_size=8) -> None:
        blocks = np.full((24, 10), 13)
        blocks = np.concatenate([np.full((24, 2), 7), blocks, np.full((24, 2), 7)], 1)
        self.blocks = np.concatenate([blocks, np.full((2, 14), 7)])
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.block_size = block_size

    def gameover_check(self):
        gameover = False
        for y in range(2, 4):
            for x in range(6, 10):
                if self.blocks[y][x] != 13:
                    gameover = True
        return gameover

    def draw(self):
        for y in range(3, self.blocks.shape[0] - 2):
            for x in range(2, self.blocks.shape[1] - 2):
                color = int(self.blocks[y][x])
                if color == 13:
                    pyxel.rect(
                        self.x_offset + self.block_size * x,
                        self.y_offset + self.block_size * (y - 3),
                        self.block_size,
                        self.block_size,
                        color,
                    )
                else:
                    pyxel.blt(
                        self.x_offset + self.block_size * x,
                        self.y_offset + self.block_size * (y - 3),
                        0,
                        8 * (color - 1),
                        0,
                        8,
                        8,
                    )

    def set_mino(self, x, y, minoshape):
        for v in range(minoshape.shape[1]):
            for u in range(minoshape.shape[0]):
                if minoshape[v][u] != 0:
                    self.blocks[y + v][x + u] = minoshape[v][u]

    def check(self):
        delete_line = 0
        for v in range(2, self.blocks.shape[0] - 2):
            for u in range(self.blocks.shape[1]):
                if self.blocks[v][u] == 13:
                    break
            else:
                self.blocks = np.delete(self.blocks, v, 0)
                delete_line += 1
                new_line = np.concatenate(
                    [np.full((1, 2), 7), np.full((1, 10), 13), np.full((1, 2), 7)], 1
                )
                self.blocks = np.concatenate([new_line, self.blocks])
        return delete_line


class NextField:
    def __init__(self, *, x_offset=0, y_offset=0, block_size=4) -> None:
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.block_size = block_size

    def draw(self, nexts):
        for n in range(5):
            for y in range(minos[nexts[n]].shape[1]):
                for x in range(minos[nexts[n]].shape[0]):
                    color = int(minos[nexts[n]][y][x])
                    if color == 0:
                        pyxel.rect(
                            self.x_offset + self.block_size * x,
                            self.y_offset
                            + self.block_size * 6 * n
                            + self.block_size * y,
                            self.block_size,
                            self.block_size,
                            13,
                        )
                    else:
                        pyxel.blt(
                            self.x_offset + self.block_size * x,
                            self.y_offset
                            + self.block_size * y
                            + self.block_size * 6 * n,
                            0,
                            4 * (color - 1),
                            24,
                            4,
                            4,
                        )


class HoldField:
    def __init__(self, *, x_offset=0, y_offset=0, block_size=4) -> None:
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.block_size = block_size

    def draw(self, hold):
        if hold == None:
            return
        for y in range(minos[hold].shape[1]):
            for x in range(minos[hold].shape[0]):
                color = int(minos[hold][y][x])
                if color == 0:
                    pyxel.rect(
                        self.x_offset + self.block_size * x,
                        self.y_offset + self.block_size * y,
                        self.block_size,
                        self.block_size,
                        13,
                    )
                else:
                    pyxel.blt(
                        self.x_offset + self.block_size * x,
                        self.y_offset + self.block_size * y,
                        0,
                        4 * (color - 1),
                        24,
                        4,
                        4,
                    )


class ActionViewer:
    def __init__(self, x_offset, y_offset) -> None:
        self.view_frame = 0
        self.action = 0
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.viewing = False

    def set_action(self, action):
        self.action = action
        self.viewing = True
        self.view_frame=pyxel.frame_count

    def update(self):
        if (pyxel.frame_count - self.view_frame) > 60:
            self.viewing = False

    def draw(self):
        if self.viewing == False:
            return
        match self.action:
            case 1:
                pyxel.text(70, 100, "Single", 0)
            case 2:
                pyxel.text(70, 100, "Double", 0)
            case 3:
                pyxel.text(70, 100, "Triple", 0)
            case 4:
                pyxel.text(70, 100, "tetris", 0)

        


if __name__ == "__main__":
    App()
