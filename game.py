import ox
import json
import tkinter as tk


class Game:
    ai_o = True 
    isOver = False
    btns = []
    with open('table.json') as fp:
        table = json.load(fp)

def find_match(origin, minState):
    a = [0]*9
    for i in range(9):
        n = minState & ox.OX[i]
        a[i] = 2 if n==ox.X[i] else 1 if n==ox.O[i] else 0
    a = [a,                                             # original
         [a[2],a[5],a[8],a[1],a[4],a[7],a[0],a[3],a[6]],# cc1
         [a[8],a[7],a[6],a[5],a[4],a[3],a[2],a[1],a[0]],# cc2
         [a[6],a[3],a[0],a[7],a[4],a[1],a[8],a[5],a[2]],# cc3
         [a[6],a[7],a[8],a[3],a[4],a[5],a[0],a[1],a[2]],# v_flip
         [a[2],a[1],a[0],a[5],a[4],a[3],a[8],a[7],a[6]],# h_flip
         [a[8],a[5],a[2],a[7],a[4],a[1],a[6],a[3],a[0]],# /_flip
         [a[0],a[3],a[6],a[1],a[4],a[7],a[2],a[5],a[8]]]# \_flip
    for state in [sum(ox.O[i]*b[i] for i in range(9)) for b in a]:
        if origin&state == origin:
            return state
    return 0

def getStateFromGrid():
    state = 0
    for i in range(9):
        ch = Game.btns[i].cget('text')
        state += ox.X[i] if ch=='X' else ox.O[i] if ch=='O' else 0
    return state

def setGridFromState(state):
    for i in range(9):
        n = state & ox.OX[i]
        Game.btns[i].config(text='X' if n==ox.X[i] else 'O' if n==ox.O[i] else '')

def process_round():
    state = getStateFromGrid()

    setGameOver(state)
    if Game.isOver:
        return

    if not Game.ai_o:
        state = ox.switchSide(state)
    minState = ox.getMinState(state)
   
    nextState,maxValue = '',0
    for key,value in Game.table[str(minState)].items():
        if nextState=='' or value>maxValue:
            nextState = key
            maxValue = value
    nextState = find_match(state, int(nextState)) 
    if not Game.ai_o:
        nextState = ox.switchSide(nextState)
    setGridFromState(nextState)
    setGameOver(nextState)


def setGameOver(state):
    msg = ''
    for o_win in ox.O_WIN:
        if state & o_win == o_win:
            msg = ('AI' if Game.ai_o else 'Player') + ' Win'
            break
        if state & (o_win*2) == (o_win*2):
            msg = ('Player' if Game.ai_o else 'AI') + ' Win'
            break

    if msg=='':
        for btn in Game.btns:
            if btn.cget('text')=='':
                return
        msg = 'Tie'
    Game.isOver = True
    '''
    root = tk.Tk()
    tk.Label(root, text=msg, font=('Helvetica',30)).pack()
    root.mainloop()
    '''

def reset():
    Game.isOver = False
    for btn in Game.btns:
        btn.config(text='')
    if Game.ai_o:
        process_round()

def changeSide():
    Game.ai_o = not Game.ai_o
    reset()

def setCell(index):
    if Game.isOver:
        return
    if Game.btns[index].cget('text')=='':
        Game.btns[index].config(text='X' if Game.ai_o else 'O')
        process_round()

if __name__=='__main__':
    
    root = tk.Tk()
    for row in range(3):
        root.grid_rowconfigure(row,weight=1)
    for col in range(4):
        root.grid_columnconfigure(col,weight=1)
    for i in range(9):
        btn = tk.Button(root, width=2, 
                        text='', font=('Helvetica',50), 
                        command = lambda i=i : setCell(i))
        btn.grid(row=i//3, column=i%3, sticky='NSEW') 
        Game.btns.append(btn)
    tk.Button(root, width=5, height=2,
              font=('Helvetica',30), text='Change', 
              command = changeSide).grid(row=0,column=3)
    tk.Button(root, width=5, height=2, 
              font=('Helvetica',30), text='Reset', 
              command = reset).grid(row=1,column=3)
    tk.Button(root, width=5, height=2, 
              font=('Helvetica',30), text='Quit', 
              command=root.destroy).grid(row=2,column=3)
    
    root.mainloop()
    
