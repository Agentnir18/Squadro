import pygame
from pygame.locals import *
import random

from piece import Piece
from utils import Utils

import time

class Chess(object):
    def __init__(self, screen, pieces_src, square_coords, square_length):
        # display surface
        self.screen = screen
        # create an object of class to show chess pieces on the board
        self.chess_pieces = Piece(pieces_src, cols=6, rows=2)
        # store coordinates of the chess board squares
        self.board_locations = square_coords
        # length of the side of a chess board square
        self.square_length = square_length
        # dictionary to keeping track of player turn
        self.turn = {"black": 0,
                     "white": 0}

        # list containing possible moves for the selected piece
        self.moves = []
        #
        self.utils = Utils()

        # mapping of piece names to index of list containing piece coordinates on spritesheet
        self.pieces = {
            "white_pawn":   5,
            "black_pawn":   11
        }

        # list containing finished pieces
        self.finished = []
        #
        self.winner = ""

        self.reset()
    
    def reset(self):
        # clear moves lists
        self.moves = []

        self.white_piece_finish = 0
        self.black_piece_finish = 0
        # randomize player turn
        x = random.randint(0, 1)
        if(x == 1):
            self.turn["black"] = 1
        elif(x == 0):
            self.turn["white"] = 1

        # two dimensonal dictionary containing details about each board location
        # storage format is [piece_name, currently_selected, x_y_coordinate]
        self.piece_location = {}
        x = 0
        for i in range(97, 105):
            a = 8
            y = 0
            self.piece_location[chr(i)] = {}
            while a>0:
                # [piece name, currently selected, board coordinates, piece reverse]
                self.piece_location[chr(i)][a] = ["", False, [x,y]]
                a = a - 1
                y = y + 1
            x = x + 1

        # reset the board
        for i in range(98, 103):
            x = 8
            while x>0:
                if(x==8):
                    self.piece_location[chr(i)][x][0] = "black_pawn"
                elif(x>2 and x<8):
                    self.piece_location[chr(103)][x][0] = "white_pawn"
                x = x - 1

    def play_turn(self):
        # white color
        white_color = (255, 255, 255)
        # create fonts for texts
        small_font = pygame.font.SysFont("comicsansms", 20)
        # create text to be shown on the game menu
        if self.turn["black"]:
            turn_text = small_font.render("Turn: Red", True, white_color)
        elif self.turn["white"]:
            turn_text = small_font.render("Turn: Yellow", True, white_color)
        
        # show welcome text
        self.screen.blit(turn_text, 
                      ((self.screen.get_width() - turn_text.get_width()) // 2,
                      10))
        
        # let player with black piece play
        if(self.turn["black"]):
            self.move_piece("black")
        # let player with white piece play
        elif(self.turn["white"]):
            self.move_piece("white")

    # method to draw pieces on the chess board
    def draw_pieces(self):
        transparent_green = (0,194,39,170)
        transparent_blue = (28,21,212,170)

        # create a transparent surface
        surface = pygame.Surface((self.square_length, self.square_length), pygame.SRCALPHA)
        surface.fill(transparent_green)

        surface1 = pygame.Surface((self.square_length, self.square_length), pygame.SRCALPHA)
        surface1.fill(transparent_blue)

        # loop to change background color of selected piece
        for val in self.piece_location.values():
            for value in val.values() :
                # name of the piece in the current location
                piece_name = value[0]
                # x, y coordinates of the current piece
                piece_coord_x, piece_coord_y = value[2]

                # change background color of piece if it is selected
                if value[1] and len(value[0]) > 5:
                    # if the piece selected is a black piece
                    if value[0][:5] == "black":
                        self.screen.blit(surface, self.board_locations[piece_coord_x][piece_coord_y])
                        if len(self.moves) > 0:
                            for move in self.moves:
                                x_coord = move[0]
                                y_coord = move[1]
                                if x_coord >= 0 and y_coord >= 0 and x_coord < 8 and y_coord < 8:
                                    self.screen.blit(surface, self.board_locations[x_coord][y_coord])
                    # if the piece selected is a white piece
                    elif value[0][:5] == "white":
                        self.screen.blit(surface1, self.board_locations[piece_coord_x][piece_coord_y])
                        if len(self.moves) > 0:
                            for move in self.moves:
                                x_coord = move[0]
                                y_coord = move[1]
                                if x_coord >= 0 and y_coord >= 0 and x_coord < 8 and y_coord < 8:
                                    self.screen.blit(surface1, self.board_locations[x_coord][y_coord])
        
        # draw all chess pieces
        for val in self.piece_location.values():
            for value in val.values() :
                # name of the piece in the current location
                piece_name = value[0]
                # x, y coordinates of the current piece
                piece_coord_x, piece_coord_y = value[2]
                # check if there is a piece at the square
                if(len(value[0]) > 1):
                    # draw piece on the board
                    self.chess_pieces.draw(self.screen, piece_name, 
                                            self.board_locations[piece_coord_x][piece_coord_y])

    def move_piece(self, turn):
        # get the coordinates of the square selected on the board
        square = self.get_selected_square()

        # if a square was selected
        if square:
            # get name of piece on the selected square
            piece_name = square[0]
            # color of piece on the selected square
            piece_color = piece_name[:5]
            # board column character
            columnChar = square[1]
            # board row number
            rowNo = square[2]
            # get x, y coordinates
            x, y = self.piece_location[columnChar][rowNo][2]
            
            # if there's a piece on the selected square
            if(len(piece_name) > 0) and (piece_color == turn):
                # find possible moves for thr piece
                if (piece_name =="black_pawn_r") or (piece_name =="white_pawn_r") :  
                    self.moves = self.rev_possible_moves(piece_name, [x,y])
                else: 
                    #print(self.piece_location) 
                    self.moves = self.possible_moves(piece_name, [x,y])

            # checkmate mechanism
            p = self.piece_location[columnChar][rowNo]
            for i in self.moves:
                if i == [x, y]:
                    if(p[0][:5] == turn) or len(p[0]) == 0:#if possible move is an empty square
                        self.validate_move([x,y])
                        if(i == [0 , y] or i == [x , 6]):
                            ColChar = chr(97 + x)#x
                            RowNo = 8 - y#y
                            if self.piece_location[ColChar][RowNo][0] == "black_pawn":
                                piece_name = self.piece_location[ColChar][RowNo][0]= "black_pawn_r"
                            elif self.piece_location[ColChar][RowNo][0] == "white_pawn":
                                piece_name = self.piece_location[ColChar][RowNo][0]= "white_pawn_r"
                        if (i == [x , 0] or i == [6 , y]):#if possible move is the finish line
                            #print(self.piece_location)
                            self.finished_piece(turn, [x,y])

            # only the player with the turn gets to play
            if(piece_color == turn):
                # change selection flag from all other pieces
                for k in self.piece_location.keys():
                    for key in self.piece_location[k].keys():
                        self.piece_location[k][key][1] = False

                # change selection flag of the selected piece
                self.piece_location[columnChar][rowNo][1] = True

    # method to find the possible moves of the selected piece
    def possible_moves(self, piece_name, piece_coord):
        # list to store possible moves of the selected piece
        positions = []
        # find the possible locations to put a piece
        if len(piece_name) > 0:
            # get x, y coordinate
            x_coord, y_coord = piece_coord
            
            # calculate moves for pawn
            if piece_name[6:] == "pawn":
                # convert list index to dictionary key
                columnChar = chr(97 + x_coord)
                rowNo = 8 - y_coord

                # calculate moves for black pawn
                if piece_name == "black_pawn":
                    if y_coord + 1 < 7:
                        
                        if(self.piece_location[columnChar][rowNo - 1][0][6:] == "pawn" or self.piece_location[columnChar][rowNo - 1][0][6:] == "pawn_r"):#if there is 1 pawn in front
                            if(self.piece_location[columnChar][rowNo - 2][0][6:] == "pawn" or self.piece_location[columnChar][rowNo - 2][0][6:] == "pawn_r"):#if there is 2 pawns in front
                                if y_coord + 3 > 6:
                                    positions.append([x_coord, 6])
                                if(self.piece_location[columnChar][rowNo - 3][0][6:] == "pawn" or self.piece_location[columnChar][rowNo - 3][0][6:] == "pawn_r"):#if there is 2 pawns in front
                                    pass
                                else:
                                    positions.append([x_coord, y_coord+3])
                            elif y_coord + 2 > 6:
                                positions.append([x_coord, 6])
                            else:
                                positions.append([x_coord, y_coord+2])

                        elif x_coord == 1 or x_coord == 5:#3 steps ahead
                            if y_coord + 3 > 6:
                                positions.append([x_coord, 6])
                            else:
                                if(self.piece_location[columnChar][rowNo - 3][0][6:] == "pawn" or self.piece_location[columnChar][rowNo - 3][0][6:] == "pawn_r"):#if there is a pawn to overlap
                                    pass
                                    #else:
                                        #positions.append([x_coord, y_coord+4])
                                else:
                                    positions.append([x_coord, y_coord+3])

                        elif x_coord == 2 or x_coord == 4:#1 step ahead
                                positions.append([x_coord, y_coord+1])

                        elif x_coord == 3:#2 step ahead
                            if y_coord + 2 > 6:
                                positions.append([x_coord, 6])
                            else:
                                if(self.piece_location[columnChar][rowNo - 2][0][6:] == "pawn" or self.piece_location[columnChar][rowNo - 2][0][6:] == "pawn_r"):#if there is a pawn to overlap
                                    if(self.piece_location[columnChar][rowNo - 3][0][6:] == "pawn" or self.piece_location[columnChar][rowNo - 3][0][6:] == "pawn_r"):#if there is 2 pawns in front
                                        pass
                                    else:
                                        positions.append([x_coord, y_coord+3])
                                else:
                                    positions.append([x_coord, y_coord+2])
                             
                # calculate moves for white pawn
                elif piece_name == "white_pawn":
                    if x_coord - 1 >= 0:

                        if(self.piece_location[chr(96 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(96 + x_coord)][rowNo][0][6:] == "pawn_r"):#if there is 1 pawn in front
                            if(self.piece_location[chr(95 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(95 + x_coord)][rowNo][0][6:] == "pawn_r"):#if there is 2 pawns in front
                                if x_coord - 3 < 0:
                                    positions.append([0, y_coord])
                                if(self.piece_location[chr(94 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(94 + x_coord)][rowNo][0][6:] == "pawn_r"):
                                    pass
                                else:
                                    positions.append([x_coord-3, y_coord])
                            elif x_coord - 2 < 0:
                                positions.append([0, y_coord])
                            else:
                                positions.append([x_coord-2, y_coord])
                            
                        elif y_coord == 1 or y_coord == 5:#1 steps ahead
                            positions.append([x_coord-1, y_coord])
                            
                        elif y_coord == 2 or y_coord == 4:#3 steps ahead
                            if x_coord - 3 < 0:
                                positions.append([0, y_coord])
                            else:
                                if(self.piece_location[chr(94 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(94 + x_coord)][rowNo][0][6:] == "pawn_r"):#if there is a pawn to overlap
                                    pass
                                    #positions.append([x_coord-4, y_coord])
                                else:
                                    positions.append([x_coord-3, y_coord])
                            
                        elif y_coord == 3:#2 steps ahead
                            if x_coord - 2 < 0:
                                positions.append([0, y_coord])
                            else:
                                if(self.piece_location[chr(95 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(95 + x_coord)][rowNo][0][6:] == "pawn_r"):#if there is a pawn to overlap
                                    if(self.piece_location[chr(94 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(94 + x_coord)][rowNo][0][6:] == "pawn_r"):
                                        pass
                                    else:
                                        positions.append([x_coord-3, y_coord])
                                else:
                                    positions.append([x_coord-2, y_coord])

            # list of positions to be removed
            to_remove = []

            # remove positions that overlap other pieces of the current player
            for pos in positions:
                x, y = pos

                # convert list index to dictionary key
                columnChar = chr(97 + x)
                rowNo = 8 - y

                # find the pieces to remove
                des_piece_name = self.piece_location[columnChar][rowNo][0]
                if(des_piece_name[:5] == piece_name[:5]):
                    to_remove.append(pos)

            # remove position from positions list
            for i in to_remove:
                positions.remove(i)

        # return list containing possible moves for the selected piece
        return positions
    
    def rev_possible_moves(self, piece_name, piece_coord):
        # list to store possible moves of the selected piece
        positions = []
        # find the possible locations to put a piece
        if len(piece_name) > 0:
            # get x, y coordinate
            x_coord, y_coord = piece_coord
            
            # calculate moves for pawn
            if piece_name[6:] == "pawn_r":
                # convert list index to dictionary key
                columnChar = chr(97 + x_coord)
                rowNo = 8 - y_coord

                # calculate moves for black pawn
                if piece_name == "black_pawn_r":
                    if y_coord - 1 >= 0:
                        
                        if(self.piece_location[columnChar][rowNo + 1][0][6:] == "pawn_r" or self.piece_location[columnChar][rowNo + 1][0][6:] == "pawn"):#if there is 1 pawn in front
                            if(self.piece_location[columnChar][rowNo + 2][0][6:] == "pawn" or self.piece_location[columnChar][rowNo + 2][0][6:] == "pawn_r"):#if there is 2 pawns in front
                                if y_coord - 3 < 0:
                                    positions.append([x_coord, 0])
                                if(self.piece_location[columnChar][rowNo + 3][0][6:] == "pawn" or self.piece_location[columnChar][rowNo + 3][0][6:] == "pawn_r"):
                                    pass
                                else:
                                    positions.append([x_coord, y_coord-3])
                            elif y_coord - 2 < 0:
                                positions.append([x_coord, 0])
                            else:
                                positions.append([x_coord, y_coord-2])

                        elif x_coord == 1 or x_coord == 5:#1 steps ahead
                            positions.append([x_coord, y_coord-1])
                        
                        elif x_coord == 2 or x_coord == 4:#3 steps ahead
                            if y_coord - 3 < 0:
                                positions.append([x_coord, 0])
                            else:
                                if(self.piece_location[columnChar][rowNo + 3][0][6:] == "pawn" or self.piece_location[columnChar][rowNo + 3][0][6:] == "pawn_r"):#if there is a pawn in front
                                    pass
                                    #positions.append([x_coord, y_coord-4])
                                else:
                                    positions.append([x_coord, y_coord-3])
                                
                        elif x_coord == 3:#2 steps ahead
                            if y_coord - 2 < 0:
                                positions.append([x_coord, 0])
                            else:
                                if(self.piece_location[columnChar][rowNo + 2][0][6:] == "pawn" or self.piece_location[columnChar][rowNo + 2][0][6:] == "pawn_r"):#if there is a pawn in front
                                    if(self.piece_location[columnChar][rowNo + 3][0][6:] == "pawn" or self.piece_location[columnChar][rowNo + 3][0][6:] == "pawn_r"):
                                        pass
                                    else:
                                        positions.append([x_coord, y_coord-3])
                                else:
                                    positions.append([x_coord, y_coord-2])
                             
                # calculate moves for white pawn
                elif piece_name == "white_pawn_r":
                    if x_coord + 1 < 7:

                        if(self.piece_location[chr(98 + x_coord)][rowNo][0][6:] == "pawn_r" or self.piece_location[chr(98 + x_coord)][rowNo][0][6:] == "pawn"):#if there is 1 pawn in front
                            if(self.piece_location[chr(99 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(99 + x_coord)][rowNo][0][6:] == "pawn_r"):#if there is 2 pawns in front
                                if x_coord + 3 > 6:
                                    positions.append([6, y_coord])
                                if(self.piece_location[chr(100 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(100 + x_coord)][rowNo][0][6:] == "pawn_r"):
                                    pass
                                else:
                                    positions.append([x_coord+3, y_coord])
                            elif x_coord + 2 > 6:
                                positions.append([6, y_coord])
                            else:
                                positions.append([x_coord+2, y_coord])

                        elif y_coord == 1 or y_coord == 5:#3 steps ahead
                            if x_coord + 3 > 6:
                                positions.append([6, y_coord])
                            else:
                                if(self.piece_location[chr(100 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(100 + x_coord)][rowNo][0][6:] == "pawn_r"):#if there is a pawn to overlap
                                    pass
                                    #positions.append([x_coord+4, y_coord])
                                else:
                                    positions.append([x_coord+3, y_coord])

                        elif y_coord == 2 or y_coord == 4:#1 steps ahead
                            positions.append([x_coord+1, y_coord])

                        elif y_coord == 3:#2 steps ahead
                            if x_coord + 2 > 6:
                                positions.append([6, y_coord])
                            else:
                                if(self.piece_location[chr(99 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(99 + x_coord)][rowNo][0][6:] == "pawn_r"):#if there is a pawn in front
                                    if(self.piece_location[chr(100 + x_coord)][rowNo][0][6:] == "pawn" or self.piece_location[chr(100 + x_coord)][rowNo][0][6:] == "pawn_r"):#if there is a pawn to overlap
                                        pass
                                    else:
                                        positions.append([x_coord+3, y_coord])
                                else:
                                    positions.append([x_coord+2, y_coord])
            
            # list of positions to be removed
            to_remove = []

            # remove positions that overlap other pieces of the current player
            for pos in positions:
                x, y = pos

                # convert list index to dictionary key
                columnChar = chr(97 + x)
                rowNo = 8 - y

                # find the pieces to remove
                des_piece_name = self.piece_location[columnChar][rowNo][0]
                if(des_piece_name[:5] == piece_name[:5]):
                    to_remove.append(pos)

            # remove position from positions list
            for i in to_remove:
                positions.remove(i)

                
        return positions

    def skip_piece(self, piece_name, piece_coord):
        # get x, y coordinates
        x, y = piece_coord
        # board column character
        columnChar = chr(97 + x)
        # board row number
        rowNo = 8 - y   
        # if the piece skipped on is white or black
        if(piece_name == "white_pawn" or piece_name == "black_pawn"):
            if piece_name == "black_pawn":
                # move the source piece to the destination piece
                self.piece_location[columnChar][8][0] = piece_name
                # remove source piece from its current position
                self.piece_location[columnChar][rowNo][0] = ""
                #set the position of black pawn to start
            elif piece_name == "white_pawn":
                # move the source piece to the destination piece
                self.piece_location[chr(103)][rowNo][0] = piece_name
                # remove source piece from its current position
                self.piece_location[columnChar][rowNo][0] = ""
        # if the piece skipped on is white reverse or black reverse       
        elif (piece_name =="white_pawn_r" or piece_name == "black_pawn_r") :  
            if piece_name == "black_pawn_r":
                # move the source piece to the destination piece
                self.piece_location[columnChar][2][0] = piece_name
                # remove source piece from its current position
                self.piece_location[columnChar][rowNo][0] = ""
                #set the position of black pawn to start
            elif piece_name == "white_pawn_r":
                # move the source piece to the destination piece
                self.piece_location[chr(97)][rowNo][0] = piece_name
                # remove source piece from its current position
                self.piece_location[columnChar][rowNo][0] = ""
                #set the position of black pawn to start
                        
    def get_selected_square(self):
        # get left event
        left_click = self.utils.left_click_event()

        # if there's a mouse event
        if left_click:
            # get mouse event
            mouse_event = self.utils.get_mouse_event()
            for i in range(len(self.board_locations)):
                for j in range(len(self.board_locations)):
                    rect = pygame.Rect(self.board_locations[i][j][0], self.board_locations[i][j][1], 
                            self.square_length, self.square_length)
                    collision = rect.collidepoint(mouse_event[0], mouse_event[1])
                    if collision:
                        selected = [rect.x, rect.y]
                        # find x, y coordinates the selected square
                        for k in range(len(self.board_locations)):
                            #
                            try:
                                l = None
                                l = self.board_locations[k].index(selected)
                                if l != None:
                                    #reset color of all selected pieces
                                    for val in self.piece_location.values():
                                        for value in val.values() :
                                            # [piece name, currently selected, board coordinates]
                                            if not value[1]:
                                                value[1] = False

                                    # get column character and row number of the chess piece
                                    columnChar = chr(97 + k)
                                    rowNo = 8 - l
                                    # get the name of the 
                                    piece_name = self.piece_location[columnChar][rowNo][0]
                                    return [piece_name, columnChar, rowNo]
                            except:
                                pass
        else:
            return None


    def finished_piece(self, turn, piece_coord):#lets make this the finish pieces
        # get x, y coordinate of the destination piece
        x, y = piece_coord

        # get chess board coordinate
        columnChar = chr(97 + x)
        
        rowNo = 8 - y 

        p = self.piece_location[columnChar][rowNo]
        
        if p[0] == "white_pawn_r":
            self.piece_location[columnChar][rowNo][0] = ""
            self.white_piece_finish += 1
            print(self.white_piece_finish)
            if self.white_piece_finish == 4:
                self.winner = "Yellow"
                print("Yellow wins")
        elif p[0] == "black_pawn_r":
            self.piece_location[columnChar][rowNo][0] = ""
            self.black_piece_finish += 1
            print(self.black_piece_finish)
            if self.black_piece_finish == 4:
                self.winner = "Red"
                print("Red wins")

        # add the finished piece to list
        self.finished.append(p)

    def validate_move(self, destination):#[x,y]
        desColChar = chr(97 + destination[0])#x
        desRowNo = 8 - destination[1]#y

        for k in self.piece_location.keys():
            for key in self.piece_location[k].keys():
                board_piece = self.piece_location[k][key]

                if board_piece[1]:#selected source piece
                    # unselect the source piece
                    self.piece_location[k][key][1] = False
                    # get the name of the source piece
                    piece_name = self.piece_location[k][key][0]
                    # move the source piece to the destination piece
                    self.piece_location[desColChar][desRowNo][0] = piece_name
                    src_name = self.piece_location[k][key][0]
                    x,y = self.piece_location[k][key][2]

                    if piece_name == "black_pawn":
                        '''if x == 1 or x == 5:#3 steps ahead
                            if(self.piece_location[k][key - 1][0] == "white_pawn" or self.piece_location[k][key - 1][0] == "white_pawn_r"):
                                if(self.piece_location[k][key - 2][0] == "white_pawn" or self.piece_location[k][key - 2][0] == "white_pawn_r"):
                                    if(self.piece_location[k][key - 3][0] == "white_pawn" or self.piece_location[k][key - 3][0] == "white_pawn_r"):
                                        self.skip_piece(self.piece_location[k][key - 3][0],self.piece_location[k][key - 3][2])
                                    self.skip_piece(self.piece_location[k][key - 2][0],self.piece_location[k][key - 2][2])
                                self.skip_piece(self.piece_location[k][key - 1][0],self.piece_location[k][key - 1][2])
                            elif(self.piece_location[k][key - 2][0] == "white_pawn" or self.piece_location[k][key - 2][0] == "white_pawn_r"):
                                if(self.piece_location[k][key - 3][0] == "white_pawn" or self.piece_location[k][key - 3][0] == "white_pawn_r"):
                                        self.skip_piece(self.piece_location[k][key - 3][0],self.piece_location[k][key - 3][2])
                                self.skip_piece(self.piece_location[k][key - 2][0],self.piece_location[k][key - 2][2])
                            elif(self.piece_location[k][key - 3][0] == "white_pawn" or self.piece_location[k][key - 3][0] == "white_pawn_r"):
                                        self.skip_piece(self.piece_location[k][key - 3][0],self.piece_location[k][key - 3][2])'''
                        if x == 1 or x == 5 or x == 3:#3 or 2 steps ahead
                            if(self.piece_location[k][key - 1][0] == "white_pawn" or self.piece_location[k][key - 1][0] == "white_pawn_r"):
                                if(self.piece_location[k][key - 2][0] == "white_pawn" or self.piece_location[k][key - 2][0] == "white_pawn_r"):
                                    self.skip_piece(self.piece_location[k][key - 2][0],self.piece_location[k][key - 2][2])
                                self.skip_piece(self.piece_location[k][key - 1][0],self.piece_location[k][key - 1][2])
                            elif(self.piece_location[k][key - 2][0] == "white_pawn" or self.piece_location[k][key - 2][0] == "white_pawn_r"):
                                    self.skip_piece(self.piece_location[k][key - 2][0],self.piece_location[k][key - 2][2])
                        elif x == 2 or x == 4:#1 step ahead
                            if(self.piece_location[k][key - 1][0] == "white_pawn" or self.piece_location[k][key - 1][0] == "white_pawn_r"):
                                if(self.piece_location[k][key - 2][0] == "white_pawn" or self.piece_location[k][key - 2][0] == "white_pawn_r"):
                                    self.skip_piece(self.piece_location[k][key - 2][0],self.piece_location[k][key - 2][2])
                                self.skip_piece(self.piece_location[k][key - 1][0],self.piece_location[k][key - 1][2])

                    elif piece_name == "white_pawn":
                        if y == 1 or y == 5:#1 steps ahead
                            if(self.piece_location[chr(ord(k) - 1)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 1)][key][0] == "black_pawn_r"):
                                if(self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn_r"):
                                    self.skip_piece(self.piece_location[chr(ord(k) - 2)][key][0],self.piece_location[chr(ord(k) - 2)][key][2])
                                self.skip_piece(self.piece_location[chr(ord(k) - 1)][key][0],self.piece_location[chr(ord(k) - 1)][key][2])
                        elif y == 2 or y == 4 or y ==3:#3 or 2 step ahead
                            if(self.piece_location[chr(ord(k) - 1)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 1)][key][0] == "black_pawn_r"):
                                if (ord(k) - 2) < 97:
                                    pass
                                elif(self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn_r"):
                                    self.skip_piece(self.piece_location[chr(ord(k) - 2)][key][0],self.piece_location[chr(ord(k) - 2)][key][2])
                                self.skip_piece(self.piece_location[chr(ord(k) - 1)][key][0],self.piece_location[chr(ord(k) - 1)][key][2])
                            elif (ord(k) - 2) < 97:
                                    pass
                            elif(self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn_r"):
                                self.skip_piece(self.piece_location[chr(ord(k) - 2)][key][0],self.piece_location[chr(ord(k) - 2)][key][2]) 
                        '''elif y == 2 or y == 4:#3 step ahead
                            if(self.piece_location[chr(ord(k) - 1)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 1)][key][0] == "black_pawn_r"):
                                if(self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn_r"):
                                    if(self.piece_location[chr(ord(k) - 3)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 3)][key][0] == "black_pawn_r"):
                                        self.skip_piece(self.piece_location[chr(ord(k) - 3)][key][0],self.piece_location[chr(ord(k) - 3)][key][2])
                                    self.skip_piece(self.piece_location[chr(ord(k) - 2)][key][0],self.piece_location[chr(ord(k) - 2)][key][2])
                                self.skip_piece(self.piece_location[chr(ord(k) - 1)][key][0],self.piece_location[chr(ord(k) - 1)][key][2])
                            elif(self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 2)][key][0] == "black_pawn_r"):
                                if(self.piece_location[chr(ord(k) - 3)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 3)][key][0] == "black_pawn_r"):
                                    self.skip_piece(self.piece_location[chr(ord(k) - 3)][key][0],self.piece_location[chr(ord(k) - 3)][key][2])
                                self.skip_piece(self.piece_location[chr(ord(k) - 2)][key][0],self.piece_location[chr(ord(k) - 2)][key][2])
                            elif(self.piece_location[chr(ord(k) - 3)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) - 3)][key][0] == "black_pawn_r"):
                                self.skip_piece(self.piece_location[chr(ord(k) - 3)][key][0],self.piece_location[chr(ord(k) - 3)][key][2])'''

                    elif piece_name == "black_pawn_r":
                        if x == 1 or x == 5:#1 steps ahead
                            if(self.piece_location[k][key + 1][0] == "white_pawn_r" or self.piece_location[k][key + 1][0] == "white_pawn"):
                                if(self.piece_location[k][key + 2][0] == "white_pawn_r" or self.piece_location[k][key + 2][0] == "white_pawn"):
                                    self.skip_piece(self.piece_location[k][key + 2][0],self.piece_location[k][key + 2][2])
                                self.skip_piece(self.piece_location[k][key + 1][0],self.piece_location[k][key + 1][2])
                        elif x == 2 or x == 4 or x ==3:#2 steps ahead
                            if(self.piece_location[k][key + 1][0] == "white_pawn_r" or self.piece_location[k][key + 1][0] == "white_pawn"):
                                if(self.piece_location[k][key + 2][0] == "white_pawn_r" or self.piece_location[k][key + 2][0] == "white_pawn"):
                                    self.skip_piece(self.piece_location[k][key + 2][0],self.piece_location[k][key + 2][2])
                                self.skip_piece(self.piece_location[k][key + 1][0],self.piece_location[k][key + 1][2])
                            elif(self.piece_location[k][key + 2][0] == "white_pawn_r" or self.piece_location[k][key + 2][0] == "white_pawn"):
                                self.skip_piece(self.piece_location[k][key + 2][0],self.piece_location[k][key + 2][2])
                        '''elif x == 2 or x == 4:#3 steps ahead
                            if(self.piece_location[k][key + 1][0] == "white_pawn_r" or self.piece_location[k][key + 1][0] == "white_pawn"):
                                if(self.piece_location[k][key + 2][0] == "white_pawn_r" or self.piece_location[k][key + 2][0] == "white_pawn"):
                                    if(self.piece_location[k][key + 3][0] == "white_pawn_r" or self.piece_location[k][key + 3][0] == "white_pawn"):
                                        self.skip_piece(self.piece_location[k][key + 3][0],self.piece_location[k][key + 3][2])
                                    self.skip_piece(self.piece_location[k][key + 2][0],self.piece_location[k][key + 2][2])
                                self.skip_piece(self.piece_location[k][key + 1][0],self.piece_location[k][key + 1][2])
                            elif(self.piece_location[k][key + 2][0] == "white_pawn_r" or self.piece_location[k][key + 2][0] == "white_pawn"):
                                if(self.piece_location[k][key + 3][0] == "white_pawn_r" or self.piece_location[k][key + 3][0] == "white_pawn"):
                                    self.skip_piece(self.piece_location[k][key + 3][0],self.piece_location[k][key + 3][2])
                                self.skip_piece(self.piece_location[k][key + 2][0],self.piece_location[k][key + 2][2])
                            elif(self.piece_location[k][key + 3][0] == "white_pawn_r" or self.piece_location[k][key + 3][0] == "white_pawn"):
                                        self.skip_piece(self.piece_location[k][key + 3][0],self.piece_location[k][key + 3][2])'''      
                    
                    elif piece_name == "white_pawn_r":
                        '''if y == 1 or y == 5:#3 steps ahead
                            if(self.piece_location[chr(ord(k) + 1)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 1)][key][0] == "black_pawn_r"):
                                if(self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn_r"):
                                    if(self.piece_location[chr(ord(k) + 3)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 3)][key][0] == "black_pawn_r"):
                                        self.skip_piece(self.piece_location[chr(ord(k) + 3)][key][0],self.piece_location[chr(ord(k) + 3)][key][2])
                                    self.skip_piece(self.piece_location[chr(ord(k) + 2)][key][0],self.piece_location[chr(ord(k) + 2)][key][2])
                                self.skip_piece(self.piece_location[chr(ord(k) + 1)][key][0],self.piece_location[chr(ord(k) + 1)][key][2])
                            elif(self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn_r"):
                                if(self.piece_location[chr(ord(k) + 3)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 3)][key][0] == "black_pawn_r"):
                                    self.skip_piece(self.piece_location[chr(ord(k) + 3)][key][0],self.piece_location[chr(ord(k) + 3)][key][2])
                                self.skip_piece(self.piece_location[chr(ord(k) + 2)][key][0],self.piece_location[chr(ord(k) + 2)][key][2])
                            if(self.piece_location[chr(ord(k) + 3)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 3)][key][0] == "black_pawn_r"):
                                self.skip_piece(self.piece_location[chr(ord(k) + 3)][key][0],self.piece_location[chr(ord(k) + 3)][key][2])'''
                        if y == 1 or y == 5 or y == 3:#2 steps ahead
                            if(self.piece_location[chr(ord(k) + 1)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 1)][key][0] == "black_pawn_r"):
                                if(self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn_r"):
                                    self.skip_piece(self.piece_location[chr(ord(k) + 2)][key][0],self.piece_location[chr(ord(k) + 2)][key][2])
                                self.skip_piece(self.piece_location[chr(ord(k) + 1)][key][0],self.piece_location[chr(ord(k) + 1)][key][2])
                            elif(self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn_r"):
                                self.skip_piece(self.piece_location[chr(ord(k) + 2)][key][0],self.piece_location[chr(ord(k) + 2)][key][2])
                        elif y == 2 or y == 4:#1 steps ahead
                            if(self.piece_location[chr(ord(k) + 1)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 1)][key][0] == "black_pawn_r"):
                                if(self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn" or self.piece_location[chr(ord(k) + 2)][key][0] == "black_pawn_r"):
                                    self.skip_piece(self.piece_location[chr(ord(k) + 2)][key][0],self.piece_location[chr(ord(k) + 2)][key][2])
                                self.skip_piece(self.piece_location[chr(ord(k) + 1)][key][0],self.piece_location[chr(ord(k) + 1)][key][2])
                    
                    # remove source piece from its current position
                    self.piece_location[k][key][0] = ""
                    # change turn
                    if(self.turn["black"]):
                        self.turn["black"] = 0
                        self.turn["white"] = 1
                    elif("white"):
                        self.turn["black"] = 1
                        self.turn["white"] = 0

                    src_location = k + str(key)
                    des_location = desColChar + str(desRowNo)
                    print("{} moved from {} to {}".format(src_name,  src_location, des_location))