from abc import ABCMeta, abstractmethod
from enum import Enum, auto
import math
from typing import List, Tuple, Callable

import pygame

FILES = 12
TOTAL_FILES = 2 * FILES
RANKS = 8

def signum(x, default: int = 0) -> int:
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return default


def figure_mapping(figures: List["Figure"]):
    return {f.pos: f for f in figures}


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
        self.surface = ChesssBoard.IMAGES[self.label].convert_alpha()
        self.moved = False    # needed for castling
        
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"], my_figures: List["Figure"]) -> List[Tuple[int, int]]:
        raise NotImplementedError()
    
class Rook(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "r" if white else "R", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"], my_figures: List["Figure"]) -> List[Tuple[int, int]]:
        opp_pos_map = figure_mapping(opponents_figures)
        pos_map = figure_mapping(my_figures)
        
        if new_pos[0] == self.pos[0]:  # same rank
            s = signum(new_pos[1] - self.pos[1]) 
            path = [(self.pos[0], i) for i in range(self.pos[1], new_pos[1] + s * 1, s)]
            path = path[1:]
            for pos in path:
                if pos in pos_map.keys():
                    return []
                elif pos != path[-1] and pos in opp_pos_map.keys():
                    return []

            return path
        
        elif new_pos[1] != self.pos[1]:
            return []
        
        path = [self.pos]
        i = self.pos[0]
        while path[-1] != new_pos:
            i = (i + 1) % (2 * FILES) 
            path.append((i, self.pos[1]))
            
        path = path[1:]

        for pos in path:
            if pos in pos_map.keys():
                break
            elif pos != path[-1] and pos in opp_pos_map.keys():
                break
        else:
            return path

        path = [self.pos]
        i = self.pos[0]
        while path[-1] != new_pos:
            i = (i - 1) % (2 * FILES) 
            path.append((i, self.pos[1]))

        path = path[1:]
        for pos in path:
            if pos in pos_map.keys():
                return []
            elif pos != path[-1] and pos in opp_pos_map.keys():
                return []

        return path 

class Knight(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "n" if white else "N", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], _, my_figures: List[Figure]) -> List[Tuple[int, int]]:
        if (abs(new_pos[0] - self.pos[0]) == 1 and abs(new_pos[1] - self.pos[1]) == 2) or (abs(new_pos[0] - self.pos[0]) == 2 and abs(new_pos[1] - self.pos[1]) == 1):
            pos_map = figure_mapping(my_figures)
            if new_pos not in pos_map.keys():
                return [new_pos]
        return []

class Bishop(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "b" if white else "B", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List[Figure], my_figures: List[Figure]) -> List[Tuple[int, int]]:
        diff = abs(new_pos[0] - self.pos[0])
        sf = signum(new_pos[0] - self.pos[0]) 
        if diff >= RANKS:
            sf = -sf
        sr = signum(new_pos[1] - self.pos[1]) 
        
        f = self.pos[0]
        r = self.pos[1]
        path = [self.pos]
        while path[-1] != new_pos:
            if len(path) >= 1:
                if new_pos[0] == f or new_pos[1] == r:
                    return []  # can't be a legal move if one of them is hitting the coordinate and the other one doesn't

            f = (f + sf) % (2 * FILES) 
            r = (r + sr) % RANKS 
            path.append((f, r))

        path = path[1:]

        pos_map = figure_mapping(my_figures)
        opp_pos_map = figure_mapping(opponents_figures)

        for pos in path:
            if pos in pos_map.keys():
                print(pos)
                return []
            elif pos != path[-1] and pos in opp_pos_map.keys():
                print(pos)
                return []

        return path


class Queen(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "q" if white else "Q", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)

    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"], my_figures: List[Figure]) -> List[Tuple[int, int]]:
        rook_path = Rook.move_path(self, new_pos, opponents_figures, my_figures)  # really dangerous; ik
        if rook_path:
            return rook_path
        
        bishop_path = Bishop.move_path(self, new_pos, opponents_figures, my_figures)  # really dangerous; ik
        return bishop_path


class King(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "k" if white else "K", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
        self.castle_one = ((start_file - 2 - (not white)) % (2 * FILES), start_rank)
        self.castle_two = ((start_file + 3 - (not white)) % (2 * FILES), start_rank)
        print(self.label, self.pos, self.castle_one, self.castle_two)
    
    def move_path(self, new_pos: Tuple[int, int], _, my_figures: List["Figure"]) -> List[Tuple[int, int]]:
        if abs(new_pos[0] - self.pos[0]) <= 1 and abs(new_pos[1] - self.pos[1]) <= 1:
            figure_map = figure_mapping(my_figures)
            if new_pos not in figure_map.keys():
                return [new_pos]
        
        return []


class Pawn(Figure):
    def __init__(self, start_file: int, start_rank: int, white: bool, font: pygame.font.Font):
        Figure.__init__(self, start_file, start_rank, "p" if white else "P", font, ChesssBoard.COLOR_WHITE if white else ChesssBoard.COLOR_BLACK)
    
    def move_path(self, new_pos: Tuple[int, int], opponents_figures: List["Figure"], _) -> List[Tuple[int, int]]:
        if self.pos[0] != new_pos[0]:
            if self.pos[1] - new_pos[1] != 1:
                return []
            
            for o_piece in opponents_figures:
                if o_piece.pos == new_pos:
                    return [new_pos]
            else:
                return []
        
        if self.pos[1] == 6 and self.pos[1] - new_pos[1] == 2: 
            return [(self.pos[0], self.pos[1] + 1), new_pos]
        
        elif self.pos[1] - new_pos[1] == 1:
            for o_piece in opponents_figures:
                if o_piece.pos == new_pos:
                    return []

            return [new_pos]
        return []
            


class ChesssBoard():

    COLOR_BLACK = [255, 0, 0]
    COLOR_WHITE = [255, 255, 255]
    
    WHITE_TURN = 0
    BLACK_TURN = 1

    IMAGES = {
        "q": pygame.image.load("pieces/wQueen.png"),
        "Q": pygame.image.load("pieces/bQueen.png"),
        "k": pygame.image.load("pieces/wKing.png"),
        "K": pygame.image.load("pieces/bKing.png"),
        "r": pygame.image.load("pieces/wRook.png"),
        "R": pygame.image.load("pieces/bRook.png"),
        "b": pygame.image.load("pieces/wBishop.png"),
        "B": pygame.image.load("pieces/bBishop.png"),
        "n": pygame.image.load("pieces/wKnight.png"),
        "N": pygame.image.load("pieces/bKnight.png"),
        "p": pygame.image.load("pieces/wPawn.png"),
        "P": pygame.image.load("pieces/bPawn.png"),
    }
    
    def __init__(self):
        font = pygame.font.Font(pygame.font.get_default_font(), 25)
        font.set_bold(True)
        self.move_count = 0
        self.checked = None
        self.winner = None
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
            King(5, 7, False, font),
            Queen(6, 7, False, font),
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
        
    def move_piece(self, start: Tuple[int, int], target: Tuple[int, int]) -> bool:
        if not does_tile_exist(*start) or not does_tile_exist(*target):
            return False

        figures = self.white_pieces if self.get_player() == ChesssBoard.WHITE_TURN else self.black_pieces
        opp_figures = self.white_pieces if self.get_player() == ChesssBoard.BLACK_TURN else self.black_pieces
        for piece in figures:
            if piece.pos == start:
                selected_piece = piece
                break
        else:
            print("Invalid piece")
            return False

        path = selected_piece.move_path(target, opp_figures, figures)
        if not path:
            return False
        
        for p in opp_figures:
            if p.pos == path[-1]:
                if isinstance(p, King):
                    print("King is not killable")
                    return False

                opp_figures.remove(p)        
                break

        if selected_piece.label.lower() == "p" and selected_piece.pos[1] == 0:
            print("Promotion of a pawn. For now instant queening. No other possibility")
            figures.append(Queen(*selected_piece.pos, selected_piece.label.islower(), selected_piece.font))
            figures.remove(selected_piece)

        selected_piece.pos = path[-1]

        self.check_checkmate(figures, opp_figures, next(filter(lambda x: x.label.lower() == "k", opp_figures)))
        
        self.move_count += 1
        selected_piece.moved = True

        
        return True

    def check_checkmate(self, figures: List[Figure], opp_figures: List[Figure], king: King):
        for f in figures:
            path = f.move_path(king.pos, opp_figures, figures)
            if path:
                self.checked = path[-1]
                print("Schach " + king.label)
                break
        else:
            self.checked = None

        print("Checked:", self.checked)
            
            
    def get_player(self):
        return self.move_count % 2
 