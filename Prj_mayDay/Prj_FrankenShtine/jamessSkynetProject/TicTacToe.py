import pygame
import sys
import random
import pickle
import time
display_width,display_height = 800,600
gameDispaly = pygame.display.set_mode((display_width,display_height))
running = True
sqr_pos = [[(int(j*display_width/3),int(i * display_height / 3)) for j in range(3)] for i in range(3)]
sqr_size=(int(display_width/3),int(display_height/3))#width and height
board = [] #1darrau

VERBOSE = False
P2=1
P1 = 0
DRAW = 4
WHOSFIRST = P1
HUMAN  =7
NO_ONE =2
TRAIN = 3
SUPERVISED_TRAIN = 5 # Show the step
HUMAN_PLAY = 6
MODE = TRAIN
winner = -1

whos_turn= WHOSFIRST

o_img = pygame.image.load(".\\img_folder/o.PNG")
o_img = pygame.transform.scale(o_img, sqr_size)
x_img = pygame.image.load(".\\img_folder/x.PNG")
x_img = pygame.transform.scale(x_img, sqr_size)

win_times = {P1:0,P2:0}
draw_times =0

class Player(object): # and his name is john c.... no, Human.
    def __init__(self,ID):
        self.ID = ID
        self.q = {}
        self.last_action = None
        self.last_state = tuple([tuple(item) for item in [[2, 2, 2], [2, 2, 2], [2, 2, 2]]])
        self.ID = ID
        self.e_greedy = 0.2
    def reward_q(self,last_state,last_action,amount,result_state,alpha=0.3,gamma=0.9):
        pass
    def avail_action(self,board):
        action_tupe = tuple([i for i in range(len(board)) if board[i]==NO_ONE])
        return action_tupe
    def start_game(self):
        self.last_state = tuple([tuple(item) for item in [[2, 2, 2], [2, 2, 2], [2, 2, 2]]])
        self.last_action = None
    def turn(self):
        global board,whos_turn,n_of_turn

        for event in pygame.event.get():
            if (event.type == pygame.MOUSEBUTTONDOWN):
                mouse_pos = pygame.mouse.get_pos()
                for i in range(3):
                    for j in range(3):
                        if (sqr_pos[i][j][0] < mouse_pos[0] and sqr_pos[i][j][0] + sqr_size[0] > mouse_pos[0] and
                                    sqr_pos[i][j][1] < mouse_pos[1] and sqr_pos[i][j][1] + sqr_size[1] > mouse_pos[
                            1] and board[i*3+j] == NO_ONE):

                            board[i*3+j] = whos_turn
                            n_of_turn += 1
                            who_won(tuple(board) ,whos_turn, n_of_turn)
                            reward_consider(winner,tuple(board),p1,p2)
                            whos_turn = self.ID ^ 1


            elif (event.type == pygame.K_ESCAPE):
                esc_pause()

            if (event.type == pygame.QUIT):
                sys.exit()
                # -------------------------------------------


class AI_player(Player):
    def __init__(self,ID):
        self.q = {}
        self.last_action =None
        self.last_state = tuple([tuple(item) for item in [[2,2,2],[2,2,2],[2,2,2]]])
        self.ID = ID
        self.e_greedy = 0.2
        if WHOSFIRST == self.ID:
            self.read_q_data("tic-tac-toe_train_dump_first.txt")
        else:
            self.read_q_data("tic-tac-toe_train_dump_second.txt")
    def read_q_data(self,path):
        try:
            with open(path,'rb') as handle:
                self.q = pickle.load(handle)
        except EOFError:
            print "seems like it's your first time training"
            pass
    def turn(self):
        global board,n_of_turn,whos_turn

        self.last_state = tuple(board)
        actions = self.get_avail_action(board)
        self.last_action = self.get_action(state=self.last_state, avail_action=actions)
        board[self.last_action] = self.ID

        n_of_turn += 1
        who_won(tuple(board), whos_turn, n_of_turn)
        reward_consider(winner,tuple(board),p1,p2)
        whos_turn = self.ID ^ 1
        if(MODE==SUPERVISED_TRAIN):
            input("bingbong")

    def reward_q(self,last_state,last_action,amount,result_state,alpha = 0.3, gamma = 0.9):
        if not(last_action==None):
            prev = self.get_q(last_state,last_action)
            action_tupe =  tuple([action for action in self.avail_action(board=last_state)])

            maxqNew = max([self.get_q(result_state,action) for action in action_tupe])

            self.q[(last_state, last_action)] += ((amount+gamma*maxqNew)-prev)
    def get_action(self,state,avail_action):

        if(random.random() < self.e_greedy):
            return random.choice(avail_action)
        else:
            qs = [self.get_q(state, action) for action in avail_action]
            max_q = max(qs)

            if(qs.count(max_q)>1):
                best_choice = [i for i in range(len(qs)) if qs[i]==max_q]
                i = random.choice(best_choice)
            else:
                i = qs.index(max_q)

            return avail_action[i]
    def get_q(self,state,action):
        if self.q.get((state,action)) is None:
            self.q[(state,action)] = 0

        return self.q[(state, action)]
    def get_avail_action(self,state):
        return [i for i in range(0,8+1) if state[i]== NO_ONE]
class Random_player(Player):
    def __init__(self,ID):
        self.random_action = 0
        self.last_state = []
        self.last_action =0
        self.ID = ID
    def set_random_action(self):
        self.random_action = random.randrange(0,8+1)
    def turn(self):
        global board, n_of_turn,whos_turn

        while(True):
            self.set_random_action()
            if(self.random_action in self.avail_action(board)):
                break
        board[self.random_action] = self.ID
        n_of_turn+=1
        who_won(tuple(board), whos_turn, n_of_turn)
        reward_consider(winner, tuple(board),p1,p2)
        whos_turn = self.ID ^1

    def reward_q(self,last_state,last_action,amount,result_board):
        pass

p1 = AI_player(P1)
p2 = AI_player(P2)

def game_end_event(status):
    global running
    if VERBOSE:
        print(status)
    #if (option == 1):
    pygame.display.update()
    conti = True

    while MODE==HUMAN_PLAY and conti:

        try:
            conti = input("this is the end_result, press 0 to continue\n")

        except:
            print("(Trump adjust his mic and say) \"wrong\"")
    running = False

    #else:
    #    sys.exit()

def save_q(path,player=AI_player(None)):
    with open(path, 'wb') as f:
        pickle.dump(player.q,f)

def who_won(board,whos_turn,n_of_turn):
    global running
    global winner_determined
    global winner,win_times
    global draw_times
    for i in range(3):
        for j in range(3):
            if(board[i*3+j]!= whos_turn):
                break
            if(j==2):
                #game_end_event("P"+str(int(whos_turn)+1)+" win")
                win_times[whos_turn] +=1

                winner = whos_turn
                winner_determined = True

    for i in range(3):
        for j in range(3):
            if (board[i+j*3] != whos_turn):
                break
            if (j == 2):
                #game_end_event("P" + str(int(whos_turn)+1) + " win")
                win_times[whos_turn] += 1
                winner = whos_turn
                winner_determined = True

    if (board[0] == whos_turn and board[4] == whos_turn and board[8] == whos_turn):
        winner = whos_turn
        winner_determined = True
        win_times[whos_turn] += 1
        #game_end_event("P" + str(int(whos_turn))+1 + " win")

    if (board[2] == whos_turn and board[4] == whos_turn and board[6]==whos_turn):
        winner = whos_turn
        winner_determined = True
        win_times[whos_turn] += 1
            #game_end_event("P" + str(int(whos_turn)+1) + " win")
    if (n_of_turn >= 9 and not winner_determined):
        # game_end_event("draw")
        winner = DRAW
        draw_times += 1

def reward_consider(winner,result_board,player,other_player):
    if(player != None):

        if(winner==P1):
            player.reward_q(player.last_state,player.last_action,1,result_board)
            other_player.reward_q(other_player.last_state,other_player.last_action,-1,result_board)
        elif (winner == P2):
            player.reward_q(player.last_state, player.last_action, -1, result_board)
            other_player.reward_q(other_player.last_state, other_player.last_action, 1, result_board)
        elif(winner==DRAW):
            other_player.reward_q(other_player.last_state, other_player.last_action, 0.5,result_board)
            player.reward_q(player.last_state, player.last_action, 0.5,result_board)

        elif whos_turn == P1:
            other_player.reward_q(other_player.last_state, other_player.last_action, 0, result_board)
        elif whos_turn == P2:
            player.reward_q(player.last_state, player.last_action, 0, result_board)

def esc_pause():
    pausing = True
    while (pausing):
        print("pause")
        for event in pygame.event.get():
            if (event.type == pygame.K_ESCAPE):
                pausing= False

def mainLoop(p1,p2):
    global winner_determined,running,winner,board,whos_turn,n_of_turn
    took=0

    whos_turn = random.randrange(P1,P2+1)
    #whos_turn = P1
    initi_time = time.clock()
    #print("looping {} times".format(looped))
    board = [NO_ONE for i in range(9)]

    n_of_turn = 0
    winner=-1
    winner_determined = False
    running = True
    VISUAL = False
    p1.start_game()
    p2.start_game() #clear var
    if MODE == HUMAN_PLAY:
        VISUAL = True


    while running:
        if not MODE== HUMAN_PLAY:
            for event in pygame.event.get():
                if(event.type ==pygame.QUIT):
                    print("saving the data... b4 you quit")
                    save_q("tic-tac-toe_train_dump_first.txt", p1)
                    save_q("tic-tac-toe_train_dump_second.txt", p2)

                    sys.exit()

    #--------------------------------------------logic part
        if(whos_turn==P1):
            p1.turn()

        elif(whos_turn==P2):
            p2.turn()

    #--------------------------------------------


        if(VISUAL == True):
            gameDispaly.fill((255, 255, 255))
            for i in range(3):
                pygame.draw.aaline(gameDispaly,(0,0,0),(i*display_width/3,0),(i*display_width/3,display_height))
                pygame.draw.aaline(gameDispaly, (0, 0, 0), (0,i * display_height / 3), (display_width,i * display_height / 3))
            for i in range(3):
                for j in range(3):
                    if(board[i*3+j]==P2):
                        gameDispaly.blit(x_img,sqr_pos[i][j])
                    elif(board[i*3+j]==P1):
                        gameDispaly.blit(o_img,sqr_pos[i][j])

        if (winner == DRAW):
            game_end_event("draw")

        elif (winner == P1):
            game_end_event("p1 won")

        elif (winner == P2):
            game_end_event("p2 won")

        pygame.time.Clock().tick()
        pygame.display.update()
    #print "it took", time.clock() - inti_t
    """took += time.clock() - initi_time
    print "took avg", took / (looped + 1)"""# for speed test
if __name__ == "__main__":
    global p1,p2
    print len(p1.q),len(p2.q)
    if(input("train?\n")):
        p1 = AI_player(P1)
        p2 = AI_player(P2)
        for i in range(10000):
            mainLoop(p1,p2)
        print "saving the data...."
        save_q("tic-tac-toe_train_dump_first.txt",p1)
        save_q("tic-tac-toe_train_dump_second.txt",p2)
    print win_times.get(P1),win_times.get(P2),draw_times
    print "ALphaTOe is ready to destroy a human! mere human, are you ready ? \n... Ofcourse not!"
    MODE = HUMAN_PLAY
    p2 = AI_player(P2)
    p1 = Player(P1)

    while True:

        p1.e_greedy = 0
        p2.e_greedy = 0
        mainLoop(p1,p2)
