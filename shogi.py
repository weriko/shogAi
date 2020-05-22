# -*- coding: utf-8 -*-
"""
Created on Thu May 21 21:47:27 2020

@author: Sandu
"""

import numpy as np
import random
import pandas as pd
import serial, time
#Todo:
    # optmizing stuff?
    # Organizing into classes and modules, I guess?
#1 -- King
#2 -- Gold
#3 -- Tower
#4 -- Silver
#5 -- Knight
#6 -- Bishop
#7 -- Lance
#8 -- Pawn
#0 -- None
#------------UPGRADED----------
#10 -- Dragon
#11 -- Supa bishop
#12 -- Gold from Silver
#13 -- Gold from knight
#14 -- Gold from Lance
#15 -- Gold from Pawn

#Winning state is determined with whoever has captured the king, no checkmates or anything. 
#Opponent doesnt have to declare a mate if the king is threatened 

# "-" for facing upwards.
#Signs will work mostly for direcional purposes
#Need to optimize movement calculations zzz
#Maybe some can be calculated using masks, but eh.
#Not fancy but it works?

class Player():
    def __init__(self, s=1):
        self.pieces = []
        self.s = s #Orientation sign
        self.mov_list = []
        
class Shogi():
    def __init__(self, board_state = None, p1= None, p2 = None):
        self.p1 = p1
        self.p2 = p2
        #DICTIONARY WITH ALL MOVEMENT CHECKS. Some use functions within the class itself just to make it easier
        self.PIECES = {0: lambda pos2, pos1, s: False, 
                       #IM SORRY I INVERTED POS1 AND POS2 HERE REMEMBER TO INVER THEM FOR #1 #2 
                       1: lambda pos2, pos1, s : pos1 in [(pos2[0] + 1*s,pos2[1] + 1*s),(pos2[0] +1*s ,pos2[1] +0*s ),(pos2[0]+ 0*s ,pos2[1]+1*s ),(pos2[0]-1,pos2[1] -1*s),(pos2[0] -1*s ,pos2[1]+ 0*s ),(pos2[0]+ 0*s,pos2[1] -1*s),(pos2[0] -1*s ,pos2[1]+ 1*s),(pos2[0] -1*s,pos2[1] -1*s)],#FIX STARTING POS NAME
                       2: lambda pos2, pos1,s: pos1 in [(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],#FIX STARTING POS NAME
                       
                        6: lambda pos1, pos2,s : pos2 in self.checkBishop(pos1,s=s),#gets a diagonal with respect with pos 1.
                        
                        
                        5: lambda pos1, pos2, s: pos2 in [(pos1[0]+3*s,pos1[1]+1),(pos1[0]+3*s,pos1[1]-1)],
                        4: lambda pos1, pos2, s: pos2 in [(pos1[0]+ 1*s, pos1[1]+1*s) , (pos1[0]+1*s, pos1[1]-1*s) , (pos1[0]+1*s, pos1[1]+0*s) , (pos1[0]-1*s, pos1[1]-1*s) , (pos1[0]-1*s, pos1[1]+1*s) ],
                        
                       8:  lambda pos1, pos2, s: pos2 in [(pos1[0]+1*s,pos1[1])],
                       7: lambda pos1, pos2, s: pos2 in self.checkLance(pos1, s),
                       3: lambda pos1, pos2, s: pos2 in self.checkTower(pos1, s), #Gets  a cross
                       
                       10: lambda pos1, pos2, s: pos2 in self.checkTower(pos1, s) or pos2 in [(pos1[0]-1, pos1[1]-1),(pos1[0]+1, pos1[1]+1),(pos1[0]+1, pos1[1]-1),(pos1[0]-1, pos1[1]+1)],
                       11: lambda pos1, pos2,s : pos2 in self.checkBishop(pos1,s=s) or pos2 in [(pos1[0]+1, pos1[1]), (pos1[0], pos1[1]+1),(pos1[0]-1, pos1[1]),(pos1[0], pos1[1]-1)],
                           
                       12: lambda pos2, pos1,s: pos1 in [(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],
                       13: lambda pos2, pos1,s: pos1 in [(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],
                       14: lambda pos2, pos1,s: pos1 in [(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],
                       15: lambda pos2, pos1,s: pos1 in [(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],
                       }
        #THIS CAN BE IMPLEMENTED WITH A SIMPLE LIST BUT eh..
        
        #dictionary used to upgrade pieces
        self.PIECE_CONV= {0:0,
                          1:1,
                          2:2,
                          3:10,
                          4:12,
                          5:13,
                          6:11,
                          7:14,
                          8:15 }
        #dictionary used to place a piece. upgrades ones are placed as unupgraded ones
        self.PIECE_FROM = {0:0,
                           1:1,
                           2:2,
                           10:3,
                           4:12,
                           13:5,
                           11:6,
                           14:7,
                           15:8}
        
        if board_state == None:
            #Default shogi beggining 1state
            self.board_state = np.array([[7,5,4,2,1, 2, 4, 5, 7],
                                         [0 , 3,0 ,0 ,0 ,0 ,0 , 6,0 ],
                                         [8 , 8, 8, 8 ,8 ,8 ,8 ,8 ,8],
                                         [0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ],
                                         [0 ,0 ,0 ,0 , 0, 0, 0, 0, 0],
                                         [0 ,0 ,0 ,0 ,0 , 0, 0, 0, 0],
                                         [-8,-8,-8,-8,-8,-8 ,-8 ,-8 ,-8 ],
                                         [0 ,-6 ,0 ,0 ,0 ,0 ,0 ,-3 ,0 ],
                                         [-7 , -5, -4, -2, -1, -2, -4, -5, -7]])
            
        else:
            self.board_state = board_state
            
    def checkBishop(self,pos1,s):
        x= 1
        #This checks all diagonals with respect to the bishop position. If it finds an allied piece, it stops as it cant go further.
        #If an enemy piece is found, its position is added and then it stops, as it cant go further
        mov =[]
        try:
            while (self.board_state[pos1[0]+x][pos1[1]+x] ==0 or np.sign(self.board_state[pos1[0]+x][pos1[1]+x])==-s  )  and x<9:
                mov.append((x+pos1[0],x+pos1[1]))
                if np.sign(self.board_state[pos1[0]+x][pos1[1]+x]) ==-s:
                    break
                
                x+=1
        except:
            pass
        
    
        x=1
        try:
            while (self.board_state[pos1[0]-x][pos1[1]-x] ==0 or np.sign(self.board_state[pos1[0]-x][pos1[1]-x])==-s )  and x<9:
                mov.append((-x+pos1[0],-x+pos1[1]))
                if np.sign(self.board_state[pos1[0]-x][pos1[1]-x]) ==-s:
                    break
                
                x+=1
        except:
            pass
        x=1
      
        try:
            while (self.board_state[pos1[0]-x][pos1[1]+x]  ==0 or np.sign(self.board_state[pos1[0]-x][pos1[1]+x])==-s  )  and x<9:
                mov.append((-x+pos1[0],x+pos1[1]))
                if np.sign(self.board_state[pos1[0]-x][pos1[1]+x]) ==-s:
                    break
                
                x+=1
              
                
             
        except:
            pass
        x=1
   
        try:
            while (self.board_state[pos1[0]+x][pos1[1]-x]  ==0 or np.sign(self.board_state[pos1[0]+x][pos1[1]-x])==-s  )  and x<9:
                mov.append((x+pos1[0],-x+pos1[1]))
                if np.sign(self.board_state[pos1[0]+x][pos1[1]-x]) ==-s:
                    break
                
                x+=1
             
        except:
            pass
        return mov
    def checkProm(self, pos,s, prom = True):
        #No fancy way to create the list... to try to optimize... yeah
        
        #Checks if the moving position is within the enemy borders, if it is it upgrades. 
        if not prom:
            return 0
        if s == -1:
            if pos in [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2), (0, 3), (1, 3), (2, 3), (0, 4), (1, 4), (2, 4), (0, 5), (1, 5), (2, 5), (0, 6), (1, 6), (2, 6), (0, 7), (1, 7), (2, 7), (0, 8), (1, 8), (2, 8)]:
                return 1
            return 0
        else:
            if pos in [(6, 0), (7, 0), (8, 0), (6, 1), (7, 1), (8, 1), (6, 2), (7, 2), (8, 2), (6, 3), (7, 3), (8, 3), (6, 4), (7, 4), (8, 4), (6, 5), (7, 5), (8, 5), (6, 6), (7, 6), (8, 6), (6, 7), (7, 7), (8, 7), (6, 8), (7, 8), (8, 8)]:
                return 1
            return 0
            
        
            
    
    def checkTower(self,pos1,s):
        x=1
        mov=[]
        #todo: REMOVE TRY EXCEPT, Add a max pos limit
        
        #Similar to bishop, but instead of doing diagonals it just checks the column and row with respect on the position of the tower
        try:
            while (self.board_state[pos1[0]+x][pos1[1]] ==0 or np.sign(self.board_state[pos1[0]+x][pos1[1]]) ==-s) and x<9:
                mov.append((pos1[0]+x,pos1[1]))
                if np.sign(self.board_state[pos1[0]+x][pos1[1]]) ==-s:
                    break
                
                x+=1
        except:
            pass
        x=1
        try:
            while (self.board_state[pos1[0]][pos1[1]+x] ==0 or np.sign(self.board_state[pos1[0]][pos1[1]+x]) ==-s) and x<9:
                if np.sign(self.board_state[pos1[0]][pos1[1]+x]) ==-s:
                    break
                mov.append((pos1[0],pos1[1]+x))
                x+=1
        except:
            pass
        x=1
        try:
            while (self.board_state[pos1[0]-x][pos1[1]] ==0 or np.sign(self.board_state[pos1[0]-x][pos1[1]]) ==-s) and x<9:
                mov.append((pos1[0]-x,pos1[1]))
                if np.sign(self.board_state[pos1[0]-x][pos1[1]]) ==-s:
                    break
                
                x+=1
        except:
            pass
        x=1
        try:
            while (self.board_state[pos1[0]][pos1[1]-x] ==0 or np.sign(self.board_state[pos1[0]][pos1[1]-x]) ==-s) and x<9:
                mov.append((pos1[0],pos1[1]-x))
                if np.sign(self.board_state[pos1[0]][pos1[1]-x]) ==-s:
                    break
                
                x+=1
            return mov
        except:
            pass
    def checkLance(self,pos1, s):
        x=1
        mov=[]
        try:
            while (self.board_state[pos1[0]+x*s][pos1[1]] ==0 or np.sign(self.board_state[pos1[0]+x*s][pos1[1]]) ==-s) and x<9:
                mov.append((pos1[0]+x*s,pos1[1]))
                if np.sign(self.board_state[pos1[0]+x*s][pos1[1]]) ==-s:
                    break
                
                x+=1
        except:
            pass
        return mov
    
    
    def move(self, p, pos1, pos2):
       
        
        if pos2[0] >8 or pos2[1] >8 or pos2[0] <0 or pos2[1] <0: #Checks if pos is out of bounds.
            return 0
        
        #Check if piece belongs to player
        if (p==self.p1) and (self.board_state[pos1[0],pos1[1]]<0):
            print("Not your piece")
            return 0
        elif p==self.p2 and self.board_state[pos1[0],pos1[1]]>0:
            print("Not your piece")
            return 0

            
        #Replaces the pos2 with the new piece, and pos1 with a blank space
        try: #REMOVE THIS TRY
            if self.PIECES[np.abs(self.board_state[pos1[0],pos1[1]])](pos1,pos2,p.s) and np.sign(self.board_state[pos1[0],pos1[1]]) != np.sign(self.board_state[pos2[0],pos2[1]]):
                if self.board_state[pos2[0],pos2[1]]:
                    p.pieces.append(-self.board_state[pos2[0],pos2[1]])
                self.board_state[pos2[0],pos2[1]] = self.board_state[pos1[0],pos1[1]]
                self.board_state[pos1[0],pos1[1]] = 0
                #print("OK")
                
                if self.checkProm(pos2, p.s):
                    self.board_state[pos2[0],pos2[1]] = self.PIECE_CONV.get( np.abs(self.board_state[pos2[0],pos2[1]]), np.abs(self.board_state[pos2[0],pos2[1]]))*p.s
                return 1
            else: 
                #print("Not a valid move!")
                return 0
            
        except:
            return 0
    
      
    def place(self, p, piece, pos):
        #Checks if there is another pawn in the row. 2 pawns on the same team cant be placed on the same row
        if piece==8*p.s and p.s*8 in self.board_state[:,pos[1]]:
            print("oops")
            return 0
        #Checks if the player has the piece, and the position is empty
        if piece in p.pieces and not self.board_state[pos[0],pos[1]]:
            self.board_state[pos[0],pos[1]] = self.PIECE_FROM.get(np.abs(piece), np.abs(piece))*p.s
            
            return 1
        print("oops")
        return 0
    
    def game_human(self):
        self.board_state = np.array([[7,5,4,2,1, 2, 4, 5, 7],
                                         [0 , 3,0 ,0 ,0 ,0 ,0 , 6,0 ],
                                         [8 , 8, 8, 8 ,8 ,8 ,8 ,8 ,8],
                                         [0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ],
                                         [0 ,0 ,0 ,0 , 0, 0, 0, 0, 0],
                                         [0 ,0 ,0 ,0 ,0 , 0, 0, 0, 0],
                                         [-8,-8,-8,-8,-8,-8 ,-8 ,-8 ,-8 ],
                                         [0 ,-6 ,0 ,0 ,0 ,0 ,0 ,-3 ,0 ],
                                         [-7 , -5, -4, -2, -1, -2, -4, -5, -7]]) 
        #A human vs human game
        winner = False
        turns = [self.p1,self.p2]
        x=0
        current = turns[x]
        players = ["PLAYER 1", "PLAYER 2"]
        while not winner:
            print(self.board_state)
            valid = 0
            while not valid:
                choice = int(input(f"{players[x%2]}\n1) Move\n2)Place"))
                if choice ==1:
                    pos1 = eval(input("From where")) #Yes eval is insecure
                    pos2 = eval(input("To where"))
                    if self.move(current, pos1, pos2 ):
                        break
                elif choice ==2:
                    
                    piece = int(input("Piece number"))
                    pos = eval(input("Where"))
                    if self.place(current, piece, pos):
                        break
                else:
                    winner = 1
                    break
                    
            if 1 in self.p1.pieces or -1 in self.p2.pieces:
                winner = 1
                
            x+=1
            current = turns[x%2]
    def game_random(self):
        self.board_state = np.array([[7,5,4,2,1, 2, 4, 5, 7],
                                         [0 , 3,0 ,0 ,0 ,0 ,0 , 6,0 ],
                                         [8 , 8, 8, 8 ,8 ,8 ,8 ,8 ,8],
                                         [0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ],
                                         [0 ,0 ,0 ,0 , 0, 0, 0, 0, 0],
                                         [0 ,0 ,0 ,0 ,0 , 0, 0, 0, 0],
                                         [-8,-8,-8,-8,-8,-8 ,-8 ,-8 ,-8 ],
                                         [0 ,-6 ,0 ,0 ,0 ,0 ,0 ,-3 ,0 ],
                                         [-7 , -5, -4, -2, -1, -2, -4, -5, -7]]) 
        self.p1.pieces = []
        self.p2.pieces = []
        mov_list = []
        winner = False
        turns = [self.p1,self.p2]
        board_states = []
        x=0
        current = turns[x]
        players = ["PLAYER 1", "PLAYER 2"]
        
        
        #Yes this is a bit wasteful but eh
        #Dictionary that returns a list with the posible movements of a piece with respect of its position
        piece_mov =  {0: lambda pos, s:False,
                       #IM SORRY I INVERTED POS1 AND POS2 HERE REMEMBER TO INVER THEM FOR #1 #2 
                       1: lambda pos2, s: [(pos2[0] + 1*s,pos2[1] + 1*s),(pos2[0] +1*s ,pos2[1] +0*s ),(pos2[0]+ 0*s ,pos2[1]+1*s ),(pos2[0]-1,pos2[1] -1*s),(pos2[0] -1*s ,pos2[1]+ 0*s ),(pos2[0]+ 0*s,pos2[1] -1*s),(pos2[0] -1*s ,pos2[1]+ 1*s),(pos2[0] -1*s,pos2[1] -1*s)],#FIX STARTING POS NAME
                       2: lambda pos2, s: [(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],#FIX STARTING POS NAME
                       
                        6: lambda pos1, s: self.checkBishop(pos1,s=s),#gets a diagonal with respect with pos 1.
                        
                        
                        5:  lambda pos1, s:[(pos1[0]+3*s,pos1[1]+1),(pos1[0]+3*s,pos1[1]-1)],
                        4:  lambda pos1, s:[(pos1[0]+ 1*s, pos1[1]+1*s) , (pos1[0]+1*s, pos1[1]-1*s) , (pos1[0]+1*s, pos1[1]+0*s) , (pos1[0]-1*s, pos1[1]-1*s) , (pos1[0]-1*s, pos1[1]+1*s) ],
                        
                       8:   lambda pos1, s:[(pos1[0]+1*s,pos1[1])],
                       7:lambda pos1, s:self.checkLance(pos1, s),
                       3: lambda pos1, s:self.checkTower(pos1, s), #Gets  a cross
                       
                       10:  lambda pos1, s:self.checkTower(pos1, s) or pos2 in [(pos1[0]-1, pos1[1]-1),(pos1[0]+1, pos1[1]+1),(pos1[0]+1, pos1[1]-1),(pos1[0]-1, pos1[1]+1)],
                       11:  lambda pos1, s:self.checkBishop(pos1,s=s) or pos2 in [(pos1[0]+1, pos1[1]), (pos1[0], pos1[1]+1),(pos1[0]-1, pos1[1]),(pos1[0], pos1[1]-1)],
                           
                       12:  lambda pos1, s:[(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],
                       13:lambda pos1, s: [(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],
                       14:  lambda pos1, s:[(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],
                       15:  lambda pos1, s:[(pos2[0]+1*s,pos2[1]+1*s),(pos2[0]+1*s,pos2[1]+0*s),(pos2[0]+1*s,pos2[1]-1*s),(pos2[0]-1*s,pos2[1]+0*s), (pos2[0],pos2[1]+1),(pos2[0],pos2[1]-1)],
                       }
        
        while not winner:
            board_states.append(self.board_state)
            print(self.board_state)
            valid = 0
            while not valid:
                
                if current.pieces != []:
                    
                    choice = random.choice([0,0,0,0,1])
                else:
                    choice = 0
                    
                    
                if choice ==0:
                    try:
                        temp = np.where(np.sign(self.board_state) == current.s)
                        
                        rnd = random.randint(0,len(temp[0])-1)
                        
                        pos1 = (temp[0][rnd],temp[1][rnd])
                        
                        piece = self.board_state[pos1[0]][pos1[1]]
                       
                        pos2 = random.choice(piece_mov[np.abs(piece)](pos1, current.s))
                        if self.move(current, pos1, pos2 ):
                            mov_list.append((choice,pos1, pos2))
                            break
                    except:
                        pass
                elif choice ==1:
                    
                    piece = random.choice(current.pieces)
                   
                    rnd = random.randint(0,len(temp[0])-1)
                        
                    pos = (temp[0][rnd],temp[1][rnd])
                    
                    
                    if self.place(current, piece, pos):
                        mov_list.append((choice,piece,pos))
                        break
                else:
                    winner = 1
                    break
                    
            if 1 in self.p1.pieces or -1 in self.p2.pieces:
                print(self.board_state)
                print("WINNER IS > ", players[x%2])
                print("Movements > ",x)
                winner = 1
                return board_states, mov_list, x%2
                
            x+=1
            current = turns[x%2]
            
    

                



