import time, serial
def game_human_proteus(self):
       
        arduino = serial.Serial("COM3", 9600)
        time.sleep(1.8)
       
        self.board_state = np.array([[7,5,4,2,1, 2, 4, 5, 7],
                                         [0 , 3,0 ,0 ,0 ,0 ,0 , 6,0 ],
                                         [8 , 8, 8, 8 ,8 ,8 ,8 ,8 ,8],
                                         [0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ],
                                         [0 ,0 ,0 ,0 , 0, 0, 0, 0, 0],
                                         [0 ,0 ,0 ,0 ,0 , 0, 0, 0, 0],
                                         [-8,-8,-8,-8,-8,-8 ,-8 ,-8 ,-8 ],
                                         [0 ,-6 ,0 ,0 ,0 ,0 ,0 ,-3 ,0 ],
                                         [-7 , -5, -4, -2, -1, -2, -4, -5, -7]])
       
        #Implementation for arduino?
        winner = False
        turns = [self.p1,self.p2]
        x=0
        current = turns[x]
        players = ["PLAYER 1", "PLAYER 2"]
        while not winner:
            positions = []
            print(self.board_state)
            valid = 0
            while not valid:
                try:
                    choice = int(input(f"{players[x%2]}\n1) Move\n2)Place"))
                    if choice ==1:
                        pos1 = eval(input("From where")) #Yes eval is insecure
                        pos2 = eval(input("To where"))
                       
                        if self.move(current, pos1, pos2 ):
                            """
                            arduino.write(pos1[0])
                            arduino.write(pos1[1])
                            arduino.write(pos2[0])
                            arduino.write(pos2[1])
                            arduino.write(self.board_state[pos[0]][pos[1]])
                            arduino.write(current.sign)
                            """
                            to_send = f"{choice}{pos1[0]}{pos1[1]}{pos2[0]}{pos2[1]}{'x'+str(abs(self.board_state[pos2[0]][pos2[1]])) if abs(self.board_state[pos2[0]][pos2[1]]) < 10 else abs(self.board_state[pos2[0]][pos2[1]])}{0 if current.s == -1 else 1}"+current.pieces_to_str()
                            arduino.write(to_send.encode())
                            break
                    elif choice ==2:
                       
                        piece = int(input("Piece number"))
                        pos = eval(input("Where"))
                        if self.place(current, piece, pos):
                            positions.append(1)
                            to_send = f"{choice}{pos[0]}{pos[1]}{'x'+str(abs(self.board_state[pos[0]][pos[1]])) if abs(self.board_state[pos[0]][pos[1]]) < 10 else abs(self.board_state[pos[0]][pos[1]])}{0 if current.s == -1 else 1}  "+current.pieces_to_str()
                            arduino.write(to_send.encode())
                            break
                    else:
                        a =input("are you sure you want to quit? Y/N")
                        if a.upper() == "Y":
                            winner = 1
                            arduino.close()
                            break
                except Exception as e:
                    print(e)
                       
                   
            if 1 in self.p1.pieces or -1 in self.p2.pieces:
                winner = 1
               
            x+=1
            current = turns[x%2]
p2 = Player(s=-1)
p1 = Player()
shogi = Shogi(p1=p1,p2=p2)
shogi.game_human_proteus()
