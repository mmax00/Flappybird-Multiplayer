import client
import pygame
import threading
import random
import string

IP = input("Enter IP:")
PORT = 65432
name = input("Enter your name:")

pygame.init()

BIRD_WIDTH,BIRD_HEIGHT = 70,50
SPACING = 350
vel=10
GROUND_HEIGHT = 95
moving_speed=vel//3

class bird(object):
    def __init__(self,x,y,img,name):
        self.x = x
        self.y = y
        self.name = name
        self.text_name = font.render(name,True,(255,255,255))
        self.text_nameRect = self.text_name.get_rect()

        #Loading and scaling image
        self.img = pygame.image.load('resources/'+img)
        self.img = pygame.transform.scale(self.img,(BIRD_WIDTH,BIRD_HEIGHT))
        self.imgRect = self.img.get_rect()

        #Roatted images
        self.imgUP =pygame.transform.rotate(self.img, 30)
        self.imgDown = pygame.transform.rotate(self.img, -30)

        self.isFlapping = False
        self.isAlive = True

        self.flapp_count = 6

    def draw_bird(self):
        if self.isFlapping:
            self.img = self.imgUP
        else:
            self.img = self.imgDown

        self.imgRect = self.img.get_rect()
        self.imgRect.center = (self.x, self.y)
        win.blit(self.img, self.imgRect)

        self.text_nameRect.center = (self.x, self.y - BIRD_HEIGHT)
        win.blit(self.text_name,self.text_nameRect)

    def flap(self):
        #flap, same as jump except we dont come down; move_down function does that
        if self.flapp_count>0 and self.y > 0 + BIRD_HEIGHT // 2:
            self.y-=(self.flapp_count**2)//3
            self.flapp_count -= 1
        else:
            self.isFlapping=False
            self.flapp_count=10

    def move_down(self):
        if self.y < SCREEN_HEIGHT-BIRD_HEIGHT//2-GROUND_HEIGHT:
            self.y+=vel


    def move(self):
        #Moves the bird
        if self.isFlapping:
            self.flap()
        else:
            self.move_down()

    def check_collision(self):
        #Checks for collision if we are alive
        if self.isAlive:
            #Checks for ground collision
            if self.y>=SCREEN_HEIGHT-BIRD_HEIGHT//2-GROUND_HEIGHT-3:
                self.isAlive=False

            # Checks collision between bird and pipes
            for p in pipes:
                if self.x + BIRD_WIDTH // 2 >= p.x and self.x + BIRD_WIDTH // 2 <= p.x + p.width:
                    if self.y - BIRD_HEIGHT // 2 <= p.y - p.GAP or self.y + BIRD_HEIGHT // 2 >= p.y:
                        self.isAlive = False

            #Sends the message to server if we are dead
            if not self.isAlive:
                msg = 'dead'
                client_con.send_msg_to_server(msg)

class pipe(object):
    #Pipe object
    def __init__(self,x,y):
        self.x = x
        self.y = y

        #Width and height of pip
        self.width = 100
        self.height = 535
        #Loads the pipe upper pictue and pipe down picture and changes their size
        self.pipeDown = pygame.image.load('resources//pipeDown.png')
        self.pipeDown = pygame.transform.scale(self.pipeDown,(self.width,self.height))
        self.pipeUP = pygame.image.load('resources//pipeUp.png')
        self.pipeUP = pygame.transform.scale(self.pipeUP,(self.width,self.height))
        #Gap between upper pipe and below one
        self.GAP = 230
        #If the pipe is passed used for score
        self.passed = False


    def draw_pipe(self):
        #Draws pipe if x position is under 1000; width of the window is 500
        if self.x<1000:
            win.blit(self.pipeDown,[self.x,self.y])
            win.blit(self.pipeUP,(self.x,self.y-self.GAP-self.height))


def randomString(stringLength=5):
    #For random name
    #Used only for testing purposes
    letters = string.ascii_lowercase

    return ''.join(random.choice(letters) for i in range(stringLength))

def handle_data(data):
    data_list =[]
    prev=0
    counter=0

    #Splits data so we dont get clogged information
    data = data+'/'
    for c in data:
        if c=='/' and counter!=0:
            data_list.append(data[prev:counter])
            prev=counter
        counter+=1

    #Checks the split  data
    for d in data_list:
        print(data)
        if d[:3]=='/nc':
            #if Client has connected
            d = d[4:]
            d = d[:len(d) - 1]
            new_bird(d)
        if d[:3]=='/dc':
            #if client has disconnected
            d=d[4:]
            d = d[:len(d) - 1]
            remove_bird(d)
        if d[:2]=='/f':
            #if client sent to server space or flapping state
            d = d[3:]
            d = d[:len(d)-1]
            set_bird_flap(d)
        if d[:2]=='/q':
            #if recieved message is queue state ( number of ready palyers/number of players)
            queue_text[1]=d[3:]
        if d[:2]=='/s':
            #changes state
            change_state(d[3:])
        if d[:2]=='/p':
            #Sets y of the pipes
            handle_pipes(d[3:])

def handle_pipes(msg):
    #sets the pipes y position after recievig the message /p* (some number) * .....
    global pipes
    prev =0
    pipe_counter=0
    counter=0
    for c in msg:
        if c=='*':
            pipes[pipe_counter].y=int(msg[prev:counter])
            prev=counter+1
            pipe_counter+=1
        counter+=1

def change_state(s):
    #changes state of the game
    global state,queued
    #if the state is play we want to reset queued boolean to False so we can Q again
    if state == 'play': queued=False
    state = s

def set_bird_flap(n):
    #Sets the isFlapping boolean to true if the name of the bird is ours
    global flappybird_list
    if n != name:
        index = players_list.index(n)
        flappybird_list[index].isFlapping = True

def new_bird(name):
    #Adds new bird to the list when someone connects
    global flappybird_list,players_list
    if name not in players_list:
        players_list.append(name)
        print(players_list)
        flappybird_list.append(bird(SCREEN_WIDTH//2,SCREEN_HEIGHT//2,'flappybird.png',name))
        print(flappybird_list)

def remove_bird(name):
    #Removes the bird from the list if someone has disconnected
    global players_list,flappybird_list

    index = players_list.index(name)
    players_list.pop(index)
    flappybird_list.pop(index)
    print(players_list)

def draw_birds():
    for bird in flappybird_list:
        bird.draw_bird()

def move_birds():
    for bird in flappybird_list:
        bird.move()


def recieve_from_server():
    #Gets the yielded information from the client.recieve_from_server function
    recieved_data = client_con.recieve_from_server()
    for data in recieved_data:
        handle_data(data.decode())

def connect_to_server():
    #Connects to the server and sets the state of the game
    global state

    client_con.connect_to_server()

    client_con.send_msg_to_server(name)
    state = client_con.recieve_msg()

    print("Connected to server; Name:",name,"State:",state)

def update_server_pos():
    #NOT USED
    #updates the position of the bird on server so it can sync
    sync_msg = '/p*'+str(flappy_bird.y)
    client_con.send_msg_to_server(sync_msg)

def queue():
    #draws text in Q
    win.blit(background, (0, 0))
    win.blit(ground,(0,654))
    if not queued:
        text = ["Press", "Space", "To", "Queue"]
        counter = 0
        for t in text:
            rend = big_font.render(t, True, (255, 255, 255))
            rendRect = rend.get_rect()
            rendRect.center = (SCREEN_WIDTH // 2, 150 + counter * 150)
            win.blit(rend, rendRect)
            counter += 1
    else:
        counter = 0
        for t in queue_text:
            rend = big_font.render(t, True, (255, 255, 255))
            rendRect = rend.get_rect()
            rendRect.center = (SCREEN_WIDTH // 2, 150 + counter * 150)
            win.blit(rend, rendRect)
            counter += 1

def draw_ground():
    #draws moving ground
    global ground_x

    #Checks if we are only one on the server; if we are then someone is alive
    if len(flappybird_list)==0:
        someone_alive=True
    else:
        someone_alive = False

    #Checks if any of the players is alive
    #!!!!!!!!!!!!!!!!!!! This should change since we are not getting response from a server when someone is dead
    for fb in flappybird_list:
        if fb.isAlive or flappy_bird.isAlive:
            someone_alive =True
            break

    #moves the ground if someone is alive
    if someone_alive:
        ground_x-=moving_speed

    win.blit(ground, (ground_x, SCREEN_HEIGHT - GROUND_HEIGHT))
    #if ground is out of screen it will draw another one at the end
    if ground_x<0:
        win.blit(ground,(SCREEN_WIDTH-ground_x*(-1),SCREEN_HEIGHT - GROUND_HEIGHT))

    #if the end of the picture is off the screen, draw it at x = zero
    if ground_x<=-SCREEN_WIDTH:
        ground_x=0

def move_pipes():
    for p in pipes:
        p.x-=moving_speed

    #checks if pipe is out of the screen, if it is it will put it behind the last one and change positions in list
    #1 -> 0; 2 -> 1; 0 -> 2
    if pipes[0].x+pipes[0].width<=0:
        pipes[0].x = pipes[len(pipes)-1].x+SPACING
        temp = pipes[0]
        for i in range(1,len(pipes)):
            pipes[i-1]=pipes[i]

        pipes[len(pipes)-1]=temp
        #Changes passed parameter so it can count again for score
        pipes[len(pipes)-1].passed = False

def draw_pipes():
    for p in pipes:
        p.draw_pipe()

def start():
    global pipes,score,flappy_bird,players_list
    flappy_bird.isAlive = True
    #Adds ten pipes so it can rotate when the first is off the screen
    pipes = []
    pipes.append(pipe(1000,0))
    pipes.append(pipe(pipes[0].x + SPACING, 0))
    pipes.append(pipe(pipes[1].x + SPACING, 0))
    pipes.append(pipe(pipes[2].x + SPACING, 0))
    pipes.append(pipe(pipes[3].x + SPACING, 0))
    pipes.append(pipe(pipes[4].x + SPACING, 0))
    pipes.append(pipe(pipes[5].x + SPACING, 0))
    pipes.append(pipe(pipes[6].x + SPACING, 0))
    pipes.append(pipe(pipes[7].x + SPACING, 0))
    pipes.append(pipe(pipes[8].x + SPACING, 0))
    score = 0
    #sets players bird position to the middle
    flappy_bird.y = SCREEN_HEIGHT//2
    #sets all players to the middle position, and alive
    for bird in flappybird_list:
        bird.y = SCREEN_HEIGHT//2
        bird.isAlive = True


#Window settings
SCREEN_WIDTH,SCREEN_HEIGHT=500,750
win = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Multiplayer")
#FONTS
font = pygame.font.SysFont('resources/FlappyBirdFont.ttf', 30)
big_font = pygame.font.Font('resources/FlappyBirdFont.ttf',200)


clock = pygame.time.Clock()

client_con = client.Client(IP,PORT)
state=''

queue_text = ['Queue','']
queued = False

players_list=[] #keeps names of the connected players
flappybird_list=[]  #keeps bird objects of the connected palyers

#initializes your bird
flappy_bird = bird(SCREEN_WIDTH//2,SCREEN_HEIGHT//2,'greenfb.png',name)
#Used for moving ground
ground_x=0
#list of pipes
pipes=[]

#BACKGROUND
background = pygame.image.load('resources/background.png')
#GROUND
ground = pygame.image.load('resources/ground.png')

#Connectes to server
connect_to_server()

#starts a thread for receiving
recieving_thread = threading.Thread(target=recieve_from_server)
recieving_thread.start()

run=True
while run:
    while state == 'play':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
                state = ''
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and flappy_bird.isAlive:
                    flappy_bird.isFlapping=True
                    #notifys server when the space is pressed
                    flap_msg ='/f*'+name+'*'
                    client_con.send_msg_to_server(flap_msg)


        win.blit(background,(0,0))

        #moves everything and checks collision
        flappy_bird.move()
        move_birds()
        move_pipes()
        flappy_bird.check_collision()

        #draws everything
        draw_pipes()
        draw_ground()
        draw_birds()
        flappy_bird.draw_bird()

        #update_server_pos()

        pygame.display.update()
        #cap at 40fps
        clock.tick(40)

    #if the state is Queue
    while state == 'q':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            if event.type == pygame.KEYDOWN:
                #On space press tells the server that we are ready
                if event.key == pygame.K_SPACE and not queued:
                    msg ='ready'
                    client_con.send_msg_to_server(msg)
                    queued = True
                    start()

        #draws queue text
        queue()
        pygame.display.update()


