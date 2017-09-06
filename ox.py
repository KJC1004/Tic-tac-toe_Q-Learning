import random
import json
import os

'''
Tic-Tac-Toe AI trained with Q-Learning.



Binary Representation 00(_) 01(O) 10(X)

Eliminate all redundant states by using minimum state.
unique state == no computation wasted

Most states converged after 50000 rounds of training.

'''

table = {}

WIN = 1.5
TIE = 1.0 
LOSE = -1.0
BONUS = 0.1

O  = tuple(1*4**i for i in range(9))
X  = tuple(2*4**i for i in range(9))
OX = tuple(3*4**i for i in range(9))

O_SUM = sum(O)
X_SUM = O_SUM<<1

O_WIN = (O[0]+O[1]+O[2], O[3]+O[4]+O[5], O[6]+O[7]+O[8],
         O[0]+O[3]+O[6], O[1]+O[4]+O[7], O[2]+O[5]+O[8],
         O[0]+O[4]+O[8], O[2]+O[4]+O[6])
OX_WIN = tuple(o_win*3 for o_win in O_WIN)

def getInfo(state:int, jumpProb:int):
    '''Get next state, Predicted value and switched next state (for opponent)'''
    maxNS,predict = -1,0
    if random.random() < jumpProb:
        maxNS = random.choice(list(table[state]))
    else:
        maxValue = None
        for ns,value in table[state].items():
            if maxValue==None or value>maxValue:
                maxNS,maxValue = ns,value
    switch = getMinState(switchSide(maxNS))
    if switch in table:
        predict = -max(table[switch].values())
    return maxNS, predict, switch

def getMinState(state:int):
    '''Get the minimum equivalent state'''
    a = [0]*9
    for i in range(9):
        n = state & OX[i]
        a[i] = 2 if n==X[i] else 1 if n==O[i] else 0
    a = max(a,                                             # original
            [a[2],a[5],a[8],a[1],a[4],a[7],a[0],a[3],a[6]],# cc1
            [a[8],a[7],a[6],a[5],a[4],a[3],a[2],a[1],a[0]],# cc2
            [a[6],a[3],a[0],a[7],a[4],a[1],a[8],a[5],a[2]],# cc3
            [a[6],a[7],a[8],a[3],a[4],a[5],a[0],a[1],a[2]],# v_flip
            [a[2],a[1],a[0],a[5],a[4],a[3],a[8],a[7],a[6]],# h_flip
            [a[8],a[5],a[2],a[7],a[4],a[1],a[6],a[3],a[0]],# /_flip
            [a[0],a[3],a[6],a[1],a[4],a[7],a[2],a[5],a[8]])# \_flip
    minState = 0
    for i in range(9):
        minState += O[i]*a[i]
    return minState

def handleState(state, confirmMin=False):
    if not confirmMin:
        state = getMinState(state)
    if state not in table:
        nextStates = [getMinState(state+O[i]) for i in range(9) if state&OX[i]==0]
        table[state] = {}.fromkeys(nextStates,0)
    return state

def getReward(state:int, step:int):
    if step < 3:
        return 0
    if step > 4:
        for o_win in O_WIN:
            if (state & o_win) == o_win:
                return WIN
        if step==9:
            return TIE
    reward = 0
    for i in range(8): # 8 == len(OX_WIN)
        line1 = state & OX_WIN[i]
        if line1!=0:
            line2 = line1 & O_WIN[i]
            if line1==line2 and line2 not in O:
                reward += BONUS
    return reward 

def switchSide(state):
    return ((state & O_SUM)<<1) + ((state & X_SUM)>>1)

def train(state=0, alpha=0.5, lamb=0.9, jumpProb=0.1):
    state = handleState(state, confirmMin=False)
    for step in range(1,10): 
        nextS,predict,switch = getInfo(state, jumpProb)
        reward = getReward(nextS, step)
        table[state][nextS] += alpha*(reward+lamb*predict-table[state][nextS])
        if reward==WIN or reward==TIE:
            table[prev[0]][prev[1]] += alpha * (TIE if reward==TIE else LOSE)
            break
        else:
            prev = (state, nextS)
            state = handleState(switch,confirmMin=True)
    return nextS
    
def printState(state):
    s = ''
    for num in OX:
        n = state & num
        s += '_' if n==0 else 'O' if n in O else 'X'
    print(s[0:3]+'\n'+s[3:6]+'\n'+s[6:9])

if __name__ == '__main__':
    episode = 100000
    for i in range(episode+1):
        train(jumpProb=(episode-i)/episode)
        if i%(episode/100)==0:
            os.system('clear')
            print('{0:d}%'.format(int(i/episode*100)))
    printState(train(jumpProb=0))

    print('Number of distinct states : ',len(table))

    with open('table.json', 'w') as fp:
        json.dump(table, fp, indent=2, sort_keys=True) 

