import os
import pygame
from pygame.locals import *
from piece import Piece
from squadro import Chess
from utils import Utils

class Game:
    def __init__(self):
        # screen dimensions
        screen_width = 640
        screen_height = 750
        # flag to know if game menu has been showed
        self.menu_showed = False
        # flag to know if rules button has been pressed
        self.rules_pressed = False
        # flag to set game loop
        self.running = True
        # base folder for program resources
        self.resources = "res"
 
        # initialize game window
        pygame.display.init()
        # initialize font for text
        pygame.font.init()

        # create game window
        self.screen = pygame.display.set_mode([screen_width, screen_height])

        # title of window
        window_title = "Squadro"
        # set window caption
        pygame.display.set_caption(window_title)

        # get location of game icon
        icon_src = os.path.join(self.resources, "icon.png")
        # load game icon
        icon = pygame.image.load(icon_src)
        # set game icon
        pygame.display.set_icon(icon)
        # update display
        pygame.display.flip()
        # set game clock
        self.clock = pygame.time.Clock()


    def start_game(self):
        """Function containing main game loop""" 
        # chess board offset
        self.board_offset_x = 0
        self.board_offset_y = 50
        self.board_dimensions = (self.board_offset_x, self.board_offset_y)
        
        # get location of chess board image
        board_src = os.path.join(self.resources, "board2.png")
        # load the chess board image
        self.board_img = pygame.image.load(board_src).convert()

        # get the width of a chess board square
        square_length = self.board_img.get_rect().width // 7 

        # initialize list that stores all places to put chess pieces on the board
        self.board_locations = []

        # calculate coordinates of the each square on the board
        for x in range(0, 7):
            self.board_locations.append([])
            for y in range(0, 7):
                self.board_locations[x].append([self.board_offset_x+(x*square_length), 
                                                self.board_offset_y+(y*square_length)])

        # get location of image containing the chess pieces
        pieces_src = os.path.join(self.resources, "pieces2.png")
        # create class object that handles the gameplay logic
        self.chess = Chess(self.screen, pieces_src, self.board_locations, square_length)

        # game loop
        while self.running:
            self.clock.tick(30)
            # poll events
            for event in pygame.event.get():
                # get keys pressed
                key_pressed = pygame.key.get_pressed()
                # check if the game has been closed by the user
                if event.type == pygame.QUIT or key_pressed[K_ESCAPE]:
                    # set flag to break out of the game loop
                    self.running = False
                elif key_pressed[K_SPACE]:
                    self.chess.reset()
            
            winner = self.chess.winner

            if self.menu_showed == False:
                self.menu()
            elif len(winner) > 0:
                self.declare_winner(winner)
            elif self.rules_pressed == True:
                self.rules()
            else:
                self.game()
            
            

            # for testing mechanics of the game
            #self.game()
            #self.declare_winner(winner)

            # update display
            pygame.display.flip()
            # update events
            pygame.event.pump()

        # call method to stop pygame
        pygame.quit()
    

    def menu(self):
        """method to show game menu"""
        # background color
        bg_color = (255, 255, 255)
        # set background color
        self.screen.fill(bg_color)
        # black color
        black_color = (0, 0, 0)
        # coordinates for "Play" button
        start_btn = pygame.Rect(270, 400, 100, 50)
        # coordinates for "Rules" button
        rules_btn = pygame.Rect(270, 460, 100, 50)
        # show play button
        pygame.draw.rect(self.screen, black_color, start_btn)
        # show rules button
        pygame.draw.rect(self.screen, black_color, rules_btn)

        # white color
        white_color = (255, 255, 255)
        # create fonts for texts
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)
        # create text to be shown on the game menu
        welcome_text = big_font.render("Squadro", False, black_color)
        created_by = small_font.render("Created by Nirvan", True, black_color)
        start_btn_label = small_font.render("Play", True, white_color)
        rules_btn_label = small_font.render("Rules", True, white_color)
        # show welcome text
        self.screen.blit(welcome_text, 
                      ((self.screen.get_width() - welcome_text.get_width()) // 2, 
                      150))
        # show credit text
        self.screen.blit(created_by, 
                      ((self.screen.get_width() - created_by.get_width()) // 2, 
                      220))
        # show board game text
        self.screen.blit(small_font.render("Inspired from the actual borad game", True, black_color), 
                      ((self.screen.get_width() - created_by.get_width()) -450, 
                      self.screen.get_height() - created_by.get_height() - 20))
        # show text on the Play button
        self.screen.blit(start_btn_label, 
                      ((start_btn.x + (start_btn.width - start_btn_label.get_width()) // 2, 
                      start_btn.y + (start_btn.height - start_btn_label.get_height()) // 2)))
        # show text on the Rules button
        self.screen.blit(rules_btn_label, 
                      ((rules_btn.x + (rules_btn.width - rules_btn_label.get_width()) // 2, 
                      rules_btn.y + (rules_btn.height - rules_btn_label.get_height()) // 2)))
        # get pressed keys
        key_pressed = pygame.key.get_pressed()
        # 
        util = Utils()

        # check if left mouse button was clicked
        if util.left_click_event():
            # call function to get mouse event
            mouse_coords = util.get_mouse_event()

            # check if "Play" button was clicked
            if start_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                # change button behavior as it is hovered
                pygame.draw.rect(self.screen, white_color, start_btn, 3)
                
                # change menu flag
                self.menu_showed = True
            # check if "Rules" button was clicked
            elif rules_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                # change button behavior as it is hovered
                pygame.draw.rect(self.screen, white_color, rules_btn, 3)
                
                # change menu flag
                self.menu_showed = True
                self.rules_pressed = True
            # check if enter or return key was pressed
            elif key_pressed[K_RETURN]:
                self.menu_showed = True

    def game(self):
        # background color
        color = (0,0,0)
        # set backgound color
        self.screen.fill(color)
        
        # show the chess board
        self.screen.blit(self.board_img, self.board_dimensions)

        # call self.chess. something
        self.chess.play_turn()
        # draw pieces on the chess board
        self.chess.draw_pieces()

    def rules(self):
        # background color
        color = (255,255,255)
        # set backgound color
        self.screen.fill(color)
        # black color
        black_color = (0, 0, 0)
        # set small font
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)
        # coordinates for play again button
        back_btn = pygame.Rect(20, 20, 100, 50)
        # show reset button
        pygame.draw.rect(self.screen, black_color, back_btn)
        i = 0
        text = ["One player moves their pieces in a straight line horizontally,", 
                "while the other player only moves perpendicular to them.",
                "",
                "Each piece moves an amount of spaces shown by the dots beside",
                "its starting slot.",
                "Every turn, a player chooses one of their five pieces and moves it",
                "forward.",
                "",
                "If that piece reaches the edge of the board, it turns around, and",
                "will move the opposite direction on future turns.",
                "When either of these pieces reaches the end of the board, their",
                "movement speed is flipped.",
                "",
                "If your piece is supposed to land on or pass over one or more",
                "opponent pieces, it passes over, then lands on the next available",
                "space. Except it cant hop over a piece on the thrid position.",
                "The opponent piece (or pieces) is then sent back to whatever side",
                "it just came from.",
                "",
                "If a player gets four of their five pieces home, they win. :)"]
        self.screen.blit(big_font.render("RULES", True, black_color),(280,10))
        for line in text: 
            self.screen.blit(small_font.render(line, True, black_color),(18,(750 * 1/8)+(i*15)+(15*i)))
            i+=1

        back_label = "Back"
        back_btn_label = small_font.render(back_label, True, color)
        self.screen.blit(back_btn_label, 
                      ((back_btn.x + (back_btn.width - back_btn_label.get_width()) // 2, 
                      back_btn.y + (back_btn.height - back_btn_label.get_height()) // 2)))

         # get pressed keys
        key_pressed = pygame.key.get_pressed()
        # 
        util = Utils()

        # check if left mouse button was clicked
        if util.left_click_event():
            # call function to get mouse event
            mouse_coords = util.get_mouse_event()

            # check if reset button was clicked
            if back_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                # change button behavior as it is hovered
                pygame.draw.rect(self.screen, color, back_btn, 3)
                
                # change menu flag
                self.menu_showed = False
                self.rules_pressed = False
            # check if enter or return key was pressed
            elif key_pressed[K_RETURN]:
                self.menu_showed = False
                self.rules_pressed = False

    def declare_winner(self, winner):
        # background color
        bg_color = (255, 255, 255)
        # set background color
        self.screen.fill(bg_color)
        # black color
        black_color = (0, 0, 0)
        # coordinates for play again button
        reset_btn = pygame.Rect(250, 300, 140, 50)
        # show reset button
        pygame.draw.rect(self.screen, black_color, reset_btn)

        # white color
        white_color = (255, 255, 255)
        # create fonts for texts
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)

        # text to show winner
        text = winner + " wins!" 
        winner_text = big_font.render(text, False, black_color)

        # create text to be shown on the reset button
        reset_label = "Play Again"
        reset_btn_label = small_font.render(reset_label, True, white_color)

        # show winner text
        self.screen.blit(winner_text, 
                      ((self.screen.get_width() - winner_text.get_width()) // 2, 
                      150))
        
        # show text on the reset button
        self.screen.blit(reset_btn_label, 
                      ((reset_btn.x + (reset_btn.width - reset_btn_label.get_width()) // 2, 
                      reset_btn.y + (reset_btn.height - reset_btn_label.get_height()) // 2)))

        # get pressed keys
        key_pressed = pygame.key.get_pressed()
        # 
        util = Utils()

        # check if left mouse button was clicked
        if util.left_click_event():
            # call function to get mouse event
            mouse_coords = util.get_mouse_event()

            # check if reset button was clicked
            if reset_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                # change button behavior as it is hovered
                pygame.draw.rect(self.screen, white_color, reset_btn, 3)
                
                # change menu flag
                self.menu_showed = False
            # check if enter or return key was pressed
            elif key_pressed[K_RETURN]:
                self.menu_showed = False
            # reset game
            self.chess.reset()
            # clear winner
            self.chess.winner = ""