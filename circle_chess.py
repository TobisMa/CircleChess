from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from typing import List, Tuple, Callable

import pygame

FILES = 12
RANKS = 8


class GameState(Enum):
    RUNNING = auto()
    CANCELED = auto()
    DONE = auto()
    
def does_tile_exist(file: int, rank: int) -> bool:
    return rank != RANKS - 1 or file % FILES not in (0, 1, FILES - 2, FILES - 1)

class Figure():

    def __init__(self, start_file: int, start_rank: int,  label: str, font: pygame.font.Font, color):
        self.label = label
        self.font = font
        self.color = color
        self.pos = (start_file, start_rank)
        self.surface = self.font.render(self.label, True, self.color)
        
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"]) -> List[Tuple[int, int]]:
        raise NotImplementedError()
    
class Rook(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "r" if white else "R", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"]) -> List[int]:
        return []
    
class Knight(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "n" if white else "N", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"]) -> List[int]:
        return []

class Bishop(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "b" if white else "B", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"]) -> List[int]:
        return []


class Queen(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "q" if white else "Q", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"]) -> List[int]:
        return []


class King(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "k" if white else "K", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"]) -> List[int]:
        return []


class Pawn(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "p" if white else "P", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"]) -> List[int]:
        return []


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
            Rook(14, 7, True, font),
            Knight(15, 7, True, font),
            Bishop(16, 7, True, font),
            Queen(17, 7, True, font),
            King(18, 7, True, font),
            Bishop(19, 7, True, font),
            Knight(20, 7, True, font),
            Rook(21, 7, True, font)
        ]

        self.black_pieces: List[Figure] = [ 
            Rook(2, 7, False, font),
            Knight(3, 7, False, font),
            Bishop(4, 7, False, font),
            Queen(5, 7, False, font),
            King(6, 7, False, font),
            Bishop(7, 7, False, font),
            Knight(8, 7, False, font),
            Rook(9, 7, False, font)
        ]

        for i in range(8):
            self.white_pieces.append(
                Pawn(i + FILES + 2, 6, True, font)
            )
            self.black_pieces.append(
                Pawn(i + 2, 6, False, font)
            )
        
    def move_pieces(self, start: Tuple[int, int], target: Tuple[int, int]) -> bool:
        if not does_tile_exist(*start) or not does_tile_exist(*target):
            return False

            
        return True
            
    def get_player(self):
        return self.move_count % 2
 