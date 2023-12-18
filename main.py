# -*- coding: utf-8 -*-
from enum import Enum, auto
import math
from typing import Tuple, Union
import pygame


BACKGROUND = [147,209,255]

TWO_PI = 2 * math.pi

RANKS = 8
RANK_SIZE = 25
FILES = 10
BOARD_CENTER_OFFSET = 50

WIDTH_DEGREE = math.pi / FILES

TITLE_SCREEN_TEXT = "Welcome to circular Chess!!"


class PolarCoordinates():
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
        while phi > TWO_PI:
            phi -= TWO_PI
        
        while phi < 0:
            phi += TWO_PI
        
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
    def from_complex(cls, compl: complex) -> "PolarCoordinates":
        return cls(math.sqrt(compl.imag * compl.imag + compl.real * compl.real), math.atan2(compl.imag, compl.real))
    
    @classmethod
    def from_cartesian(cls, x: int, y: int) -> "PolarCoordinates":
        return cls.from_complex(complex(x, y))

    def __neg__(self):
        return PolarCoordinates(self.r, self.phi + math.pi)

    def __add__(self, other: "PolarCoordinates"):
        return PolarCoordinates.from_complex(complex(self) + complex(other))

    def __sub__(self, other: "PolarCoordinates"):
        return self + (-other)
    
    def __mul__(self, other: Union["PolarCoordinates", float, int]) -> "PolarCoordinates":
        if isinstance(other, (float, int)):
            return PolarCoordinates(other * self.r, self.phi)
        return PolarCoordinates(self.r * other.r, self.phi + other.phi)
    
    def __div__(self, other: Union["PolarCoordinates", float, int]) -> "PolarCoordinates":
        if isinstance(other, (float, int)):
            return PolarCoordinates(self.r / other, self.phi)
        return PolarCoordinates(self.r / other.r, self.phi - other.phi)
    
    __radd__ = __add__
    __rsub__ = __sub__
    __rmul__ = __mul__
    __rdiv__ = __div__

class GameState(Enum):
    RUNNING = auto()
    CANCELED = auto()
    DONE = auto()


def pygame_coor_to_polar(screen: pygame.Surface, x: int, y: int, scale=1) -> PolarCoordinates:
    width, height = screen.get_size()
    return scale * PolarCoordinates.from_cartesian(x - width // 2, y - height // 2)


def draw_board(screen: pygame.Surface):
        x, y = screen.get_size()
        x //= 2
        y //= 2

        
        center = PolarCoordinates(0, 0).to_cartesian(screen)
        for i in range(RANKS):
            cur_r = i * y / (RANKS + BOARD_CENTER_OFFSET / RANK_SIZE) + BOARD_CENTER_OFFSET
            new_r = (i+1) * y / (RANKS + BOARD_CENTER_OFFSET / RANK_SIZE) + BOARD_CENTER_OFFSET
            pygame.draw.circle(screen, [0, 0, 0], center, cur_r, 1)
            
            for j in range(int(cur_r), int(new_r)):
                color = [209, 152, 141] if i % 2 == 0 else [0, 0, 0]
                pygame.draw.circle(screen, color, center, j, 2)

        pygame.draw.circle(screen, [0, 0, 0], center, RANKS * y / (RANKS + BOARD_CENTER_OFFSET / RANK_SIZE) + BOARD_CENTER_OFFSET, 1)
        
        for i in range(2 * FILES):
            p = PolarCoordinates(RANKS * y / (RANKS + BOARD_CENTER_OFFSET / RANK_SIZE) + BOARD_CENTER_OFFSET, i * WIDTH_DEGREE)
            center = PolarCoordinates(BOARD_CENTER_OFFSET, i * WIDTH_DEGREE)
            # print(f"{i}. {p=} {center=}")
            pygame.draw.line(screen, [255, 255, 255], center.to_cartesian(screen), p.to_cartesian(screen), width=1)



def circle_chess(screen: pygame.Surface):
    winner = None 
    state = GameState.RUNNING

    while state is GameState.RUNNING:
        screen.fill(BACKGROUND)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                state = GameState.CANCELED
        
        draw_board(screen)

        pygame.display.flip()
    
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
