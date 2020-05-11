from shogi import *

import pandas as pd
N_GAMES = 1
games = []
PATH = "D:\\Github\\ShogiAi"


p2 = Player(s=-1)
p1 = Player()
shogi = Shogi(p1=p1,p2=p2)
states=[]
movs=[]
players=[]

for i in range(N_GAMES):
    games.append(shogi.game_random())
for x in games:
    states.append(x[0])
    movs.append(x[1])
    players.append(x[2])
df = pd.DataFrame({
    "States":states,
    "Movements":movs,
    "Players":players
    })
df.to_excel(PATH+"\\Random.xlsx") #Im a pleb who will use excel as for this excercise
    