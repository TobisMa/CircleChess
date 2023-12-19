# -*- coding: utf-8 -*-
import math
from typing import Optional, Tuple
import pygame
from polar_coordinate import PolarCoordinate
from circle_chess import ChesssBoard, GameState, FILES, RANKS, does_tile_exist


BACKGROUND = [235]*3 # [147,209,255]

FULL_CIRCLE_ANGLE = 2 * math.pi

RANK_SIZE = 25
BOARD_CENTER_OFFSET = 100

FILE_ANGLE = math.pi / FILES

TITLE_SCREEN_TEXT = "Welcome to circular Chess!!"


def pygame_coor_to_polar(screen: pygame.Surface, x: int, y: int, scale=1) -> PolarCoordinate:
    width, height = screen.get_size()
    return scale * PolarCoordinate.from_cartesian(x - width // 2, y - height // 2)


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
                    color = [209, 153, 100] if file % 2 != rank % 2 else [80, 38, 0]  

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
        pyx, pyy = coordinate.to_cartesian(screen)
        pyx -= p.surface.get_width() // 2
        pyy -= p.surface.get_height() // 2
        screen.blit(p.surface, (pyx, pyy))


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
