# -*- coding: utf-8 -*-
from enum import Enum, auto
import math
from typing import Callable, List, Optional, Tuple, Union
import pygame


BACKGROUND = [147,209,255]

FULL_CIRCLE_ANGLE = 2 * math.pi

RANKS = 8
RANK_SIZE = 25
FILES = 12
BOARD_CENTER_OFFSET = 100

FILE_ANGLE = math.pi / FILES

TITLE_SCREEN_TEXT = "Welcome to circular Chess!!"


class PolarCoordinate():
    __slots__ = ('__r', '__phi')
    def __init__(self, r: float = 1, phi: float = 0):
        self.r = r
        self.phi = phi
    
    def __repr__(self) -> str:
        return "Polar<%i * e^(%fi)>" % (self.r, self.phi)
    
    @property
    def r(self) -> float:
        return self.__r
    
    @r.setter
    def r(self, r: float):
        if r < 0:
            r = -r
            self.phi += math.pi
        self.__r = r
        
    @property
    def phi(self) -> float:
        return self.__phi
    
    @phi.setter
    def phi(self, phi: float):
        while phi > FULL_CIRCLE_ANGLE:
            phi -= FULL_CIRCLE_ANGLE
        
        while phi < 0:
            phi += FULL_CIRCLE_ANGLE
        
        self.__phi = phi
    
    def __complex__(self) -> complex:
        if self.phi == math.pi:
            return complex(-1)
        return complex(self.r * math.cos(self.phi), self.r * math.sin(self.phi))
    
    def to_cartesian(self, screen: pygame.Surface) -> Tuple[float, float]:
        x, y = screen.get_size()
        c = complex(self)
        return (c.real + x // 2, c.imag + y // 2)
    
    @classmethod
    def from_complex(cls, compl: complex) -> "PolarCoordinate":
        return cls(math.sqrt(compl.imag * compl.imag + compl.real * compl.real), math.atan2(compl.imag, compl.real))
    
    @classmethod
    def from_cartesian(cls, x: int, y: int) -> "PolarCoordinate":
        return cls.from_complex(complex(x, y))

    def __neg__(self):
        return PolarCoordinate(self.r, self.phi + math.pi)

    def __add__(self, other: "PolarCoordinate"):
        return PolarCoordinate.from_complex(complex(self) + complex(other))

    def __sub__(self, other: "PolarCoordinate"):
        return self + (-other)
    
    def __mul__(self, other: Union["PolarCoordinate", float, int]) -> "PolarCoordinate":
        if isinstance(other, (float, int)):
            return PolarCoordinate(other * self.r, self.phi)
        return PolarCoordinate(self.r * other.r, self.phi + other.phi)
    
    def __div__(self, other: Union["PolarCoordinate", float, int]) -> "PolarCoordinate":
        if isinstance(other, (float, int)):
            return PolarCoordinate(self.r / other, self.phi)
        return PolarCoordinate(self.r / other.r, self.phi - other.phi)
    
    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rdiv__ = __div__

class GameState(Enum):
    RUNNING = auto()
    CANCELED = auto()
    DONE = auto()
    

class Figure():
    def __init__(self, start_file: int, start_rank: int,  label: str, font: pygame.font.Font, color, move_check: Callable[[Tuple[int, int], Tuple[int, int]], bool]):
        self.label = label
        self.font = font
        self.color = color
        self.move_check = move_check
        self.pos = (start_file, start_rank)
        self.surface = self.font.render(self.label, True, self.color)
        
    def make_move(self, new_position: Tuple[int, int]) -> bool:
        if self.move_check(self.pos, new_position) is False:
            return False
        
        self.pos = new_position
        return True

CHECK_PAWN = lambda old, new: old[0] == new[0] and ((old[1] == 6 and new[1] == 5) or old[1] - new[1] == 1)
CHECK_ROOK = lambda old, new: old[0] == new[0] or old[1] == new[1]
CHECK_BISHOP = lambda old, new: abs(old[0] - new[0]) == abs(old[1] - new[1])
CHECK_QUEEN = lambda old, new: CHECK_ROOK(old, new) or CHECK_BISHOP(old, new)
CHECK_KING = lambda old, new: abs(old[0] - new[0]) == 1 or abs(old[1] - new[1]) == 1
CHECK_KNIGHT = lambda old, new: (abs(old[0] - new[0]) == 2 and abs(old[1] - new[1] == 1)) or (abs(old[0] - new[0]) == 1 and abs(old[1] - new[1] == 2))



    
class ChesssBoard():

    COLOR_BLACK = [255, 0, 0]
    COLOR_WHITE = [255, 255, 255]
    
    WHITE_TURN = 0
    BLACK_TURN = 1
    
    def __init__(self):
        font = pygame.font.Font(pygame.font.get_default_font(), 25)
        font.set_bold(True)
        self.move_count = 0
        self.white_pieces: List[Figure] = [
            Figure(14, 7, "t", font, ChesssBoard.COLOR_WHITE, CHECK_ROOK),
            Figure(15, 7, "n", font, ChesssBoard.COLOR_WHITE, CHECK_KNIGHT),
            Figure(16, 7, "b", font, ChesssBoard.COLOR_WHITE, CHECK_BISHOP),
            Figure(17, 7, "k", font, ChesssBoard.COLOR_WHITE, CHECK_KING),
            Figure(18, 7, "q", font, ChesssBoard.COLOR_WHITE, CHECK_QUEEN),
            Figure(19, 7, "b", font, ChesssBoard.COLOR_WHITE, CHECK_BISHOP),
            Figure(20, 7, "n", font, ChesssBoard.COLOR_WHITE, CHECK_KNIGHT),
            Figure(21, 7, "t", font, ChesssBoard.COLOR_WHITE, CHECK_ROOK)
        ]

        self.black_pieces: List[Figure] = [ 
            Figure(2, 7, "T", font, ChesssBoard.COLOR_BLACK, CHECK_ROOK),
            Figure(3, 7, "N", font, ChesssBoard.COLOR_BLACK, CHECK_KNIGHT),
            Figure(4, 7, "B", font, ChesssBoard.COLOR_BLACK, CHECK_BISHOP),
            Figure(5, 7, "K", font, ChesssBoard.COLOR_BLACK, CHECK_KING),
            Figure(6, 7, "Q", font, ChesssBoard.COLOR_BLACK, CHECK_QUEEN),
            Figure(7, 7, "B", font, ChesssBoard.COLOR_BLACK, CHECK_BISHOP),
            Figure(8, 7, "N", font, ChesssBoard.COLOR_BLACK, CHECK_KNIGHT),
            Figure(9, 7, "T", font, ChesssBoard.COLOR_BLACK, CHECK_ROOK)
        ]

        for i in range(8):
            self.white_pieces.append(
                Figure(i + FILES + 2, 6, "p", font, ChesssBoard.COLOR_WHITE, CHECK_PAWN)
            )
            self.black_pieces.append(
                Figure(i + 2, 6, "P", font, ChesssBoard.COLOR_BLACK, CHECK_PAWN)
            )
            
    def get_player(self):
        return self.move_count % 2
            

def pygame_coor_to_polar(screen: pygame.Surface, x: int, y: int, scale=1) -> PolarCoordinate:
    width, height = screen.get_size()
    return scale * PolarCoordinate.from_cartesian(x - width // 2, y - height // 2)

def does_tile_exist(file: int, rank: int) -> bool:
    return rank != RANKS - 1 or file % FILES not in (0, 1, FILES - 2, FILES - 1)

def tile_height(screen: pygame.Surface):
    return (screen.get_height() // 2) / (RANKS + BOARD_CENTER_OFFSET / RANK_SIZE)

def draw_board(screen: pygame.Surface, highlight: Optional[Tuple[int, int]], selected: Optional[Tuple[int, int]] = None):
    center_x, center_y = screen.get_size()
    center_x //= 2
    center_y //= 2
    
    for file in range(0, 2 * FILES):
        for rank in range(RANKS):
            if not does_tile_exist(file, rank):
                continue
            radius_in = rank * tile_height(screen) + BOARD_CENTER_OFFSET
            radius_out = (rank + 1) * tile_height(screen) + BOARD_CENTER_OFFSET

            for radius in range(int(radius_in), int(radius_out)):
                if selected is not None and (file, rank) == selected:
                    color = [0, 0, 255]
                elif highlight is not None and (file, rank) == highlight:
                    color = [255, 0, 0]
                else:
                    color = [209, 153, 100] if file % 2 != rank % 2 else [50, 50, 50]  

                pygame.draw.arc(screen, color, [center_x - radius, center_y - radius, 2 * radius, 2 * radius], file * FILE_ANGLE, (file + 1) * FILE_ANGLE)

def polar_to_tile(polar: PolarCoordinate, screen: pygame.Surface, scale=RANK_SIZE, offset=BOARD_CENTER_OFFSET, angle_section=FILE_ANGLE) -> Optional[Tuple[int, int]]:
    if polar.r < offset or polar.r > 2 * RANKS * tile_height(screen):
        return None
    res =  (
        int((FULL_CIRCLE_ANGLE - polar.phi) / FILE_ANGLE),
        int((polar.r - offset) / tile_height(screen)),
    )
    if not does_tile_exist(*res):
        return None
    return res

def tile_to_polar(tile: Tuple[int, int], screen: pygame.Surface) -> PolarCoordinate:
    file, rank = tile
    t_height = tile_height(screen)
    coordinate = PolarCoordinate(
        rank * t_height + BOARD_CENTER_OFFSET,
        -file * FILE_ANGLE + FULL_CIRCLE_ANGLE - FILE_ANGLE / 2
    )

    return coordinate

    
def draw_pieces(screen: pygame.Surface, game: ChesssBoard):
    for p in game.white_pieces + game.black_pieces:
        coordinate = tile_to_polar(p.pos, screen)
        coordinate.r += 0.5 * tile_height(screen)
        screen.blit(p.surface, coordinate.to_cartesian(screen))


def circle_chess(screen: pygame.Surface):
    winner = None 
    state = GameState.RUNNING

    clock = pygame.time.Clock()

    cursor_hover = None

    game = ChesssBoard()
    selected = None

    while state is GameState.RUNNING:
        screen.fill(BACKGROUND)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                state = GameState.CANCELED
            elif e.type == pygame.MOUSEMOTION:
                mouse_position = e.pos
                cursor_hover = polar_to_tile(pygame_coor_to_polar(screen, *mouse_position), screen)
            
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                cursor_tile = polar_to_tile(pygame_coor_to_polar(screen, *e.pos), screen)
                pieces = game.white_pieces if game.get_player() == ChesssBoard.WHITE_TURN else game.black_pieces

                for p in pieces:
                    if p.pos == cursor_tile:
                        selected = cursor_tile
                        break
                else:
                    print(cursor_tile)
                    print("No piece from the current player")

        
        draw_board(screen, cursor_hover, selected)
        
        draw_pieces(screen, game)

        pygame.display.flip()

        clock.tick(60)
    
    return winner
    
def main():
    pygame.init()

    screen = pygame.display.set_mode([800, 600], pygame.RESIZABLE)

    running = True
    
    count = 1

    pygame.font.init()
    font_name = pygame.font.get_default_font()
    font_obj = pygame.font.Font(font_name, 36)
    text = font_obj.render(TITLE_SCREEN_TEXT, True, [0, 0, 0])
    text_width, text_height = font_obj.size(TITLE_SCREEN_TEXT)
    
    while running:
        screen.fill(BACKGROUND)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEMOTION:
                x, y = event.pos
            
            elif event.type == pygame.KEYDOWN:
                # acutal game
                circle_chess(screen)
                ...
        
        width, height = screen.get_size()
        screen.blit(text, (width / 2 - text_width / 2, height - (height / (2 * text_height)) * text_height))
        pygame.display.flip()
            
    pygame.quit()

if __name__ == "__main__":
    main()
