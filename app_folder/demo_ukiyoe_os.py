import pygame
import os
import time
import random as rand
import new as image 


#section1: N-back test informance
def sign(a):#a as a array with no more than 4 elements

    #true flag if the element is no less than 4

    return True if len(a) != 4 else a[-1] == a[0]

    #orelse it will judge the boundaries of the array

#addition: queue insert
def insert(data,a):

    if len(a) == 4:
        a.pop(0)
    a.append(data)

    return a
    
#section 2: game interface definition
current_path = os.path.dirname(__file__)
image_path = os.path.join(current_path, 'Game')
ukiyoe_path = os.path.join(current_path, "ukiyoe")
# 2-1 scene of monster and other BG
char_1 = pygame.image.load(os.path.join(image_path,'cha-1.png'))
over_scene = pygame.image.load(os.path.join(image_path,"game_over_1.png"))
wall = pygame.image.load(os.path.join(image_path,"ground.png"))
get_ready =  pygame.image.load(os.path.join(image_path,'bg.jpg'))
game_over =  pygame.image.load(os.path.join(image_path,'bg.jpg'))
#monster on walk
ukiyoe_monster_1 = pygame.image.load(os.path.join(ukiyoe_path,"mon-1.png"))
ukiyoe_monster_2 = pygame.image.load(os.path.join(ukiyoe_path,"mon-2.png"))
ukiyoe_monster_3 = pygame.image.load(os.path.join(ukiyoe_path,"mon-3.png"))
ukiyoe_monster_4 = pygame.image.load(os.path.join(ukiyoe_path,"mon-4.png"))
ukiyoe_monster1 = [ukiyoe_monster_1] * 8
ukiyoe_monster2 = [ukiyoe_monster_2] * 8
ukiyoe_monster3 = [ukiyoe_monster_3] * 8
ukiyoe_monster4 = [ukiyoe_monster_4] * 8
rule_pic =  pygame.image.load(os.path.join(image_path,'bg.jpg'))
pause_pic =  pygame.image.load(os.path.join(image_path,'bg.jpg'))
#randomly ukiyoe-images with different effect
scene_1 = pygame.image.load(os.path.join(ukiyoe_path,"bg-1.jpg"))
scene_2 = pygame.image.load(os.path.join(ukiyoe_path,"bg-2.jpg"))
scene_3 = pygame.image.load(os.path.join(ukiyoe_path,"bg-3.jpg"))
scene = [scene_1, scene_2, scene_3]
#button class to press
class button():
    def __init__(self, color, x,y,width,height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self,win,outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

#transfer size of the monsters
def change_size(chars, x , y):
    for i in range(len(chars)):
        chars[i] = pygame.transform.scale(chars[i],(x,y))
    return chars

ukiyoe_monster1 = change_size(ukiyoe_monster1, 90, 90)
ukiyoe_monster2 = change_size(ukiyoe_monster2, 90, 90)
ukiyoe_monster3 = change_size(ukiyoe_monster3, 90, 90)
ukiyoe_monster4 = change_size(ukiyoe_monster4, 90, 90)

scene = change_size(scene, 500, 480)

#enemy edition

class enemy(object):
    def __init__(self, x, y, left_data, char1, id):
        self.x ,self.y = x + 22 , y + 22
        self.char = char1
        self.left_data = left_data
        self.left = True
        self.walkCount = 0
        self.speed = 30 #check if it is too slow or not
        self.time = time.time()
        self.show = True
        self.id = id
    #with flash setting on the character
    def draw_mimic(self, win):
        if not self.show:
            return
        speed1 = self.speed
        if self.walkCount + 1 >= 24:
            self.walkCount = 0
        
        if self.left:
            self.x -= speed1
            win.blit(self.left_data[self.walkCount//3], (self.x,self.y))
            self.walkCount += 1
        else:
            win.blit(self.char,(self.x, self.y))
    #vanish until it is off screed
    def vanish(self):
        if self.x < -50:
            self.show = False
    #call the id of the monster
    def call_id(self):

        return self.id

#other image selection

set_same = button((0,255,0),0,420,50,50,"T")
set_different = button((0,255,0),400,420,50,50,"F")
set_right = pygame.image.load(os.path.join(image_path,'correct.jpeg'))
set_wrong = pygame.image.load(os.path.join(image_path,'cross.png'))
set_right = pygame.transform.scale(set_right,(50,50))
set_wrong = pygame.transform.scale(set_wrong,(50,50))

activate_choice = True
same_flag = True
activate_result = True
right_flag = True
event = "no event"

#settings could be changed
sum_time = 32

#correct rate
correct_time, total_time = 0, 0 
correct_flag = False
back_value = []

# flag on track
class senario_setting(object):
    
    def  __init__(self):
        self.flag_1, self.flag_2, self.flag_3 = False, False, False
        self.flag_4, self.flag_5 = False, False
    
    def scene(self):
        if self.flag_1:
            return self.scenario_1

        elif self.flag_2:
            return self.scenario_2

        elif self.flag_3:
            return self.scenario_3

        elif self.flag_4:
            return self.scenario_4
        
        else:
            return self.scenario_5

#monster basic
class init_setting_2(object):
    
    def __init__(self, char):
        self.char = char
        self.enemy1 = enemy(480, 320, self.char[0], self.char[0][0], "A")
        self.enemy2 = enemy(480, 320, self.char[1], self.char[0][0], "B")
        self.enemy3 = enemy(480, 320, self.char[2], self.char[0][0], "C")
        self.enemy4 = enemy(480, 320, self.char[3], self.char[0][0], "D")
        self.flag = [False] * 4
        self.enemy = [self.enemy1, self.enemy2, self.enemy3, self.enemy4]


    def set_flag(self):
        return [self.enemy1.show, self.enemy2.show, self.enemy3.show, self.enemy4.show]

#init python
run = True
pygame.init()
clock = pygame.time.Clock()
width, length = 500, 480
win = pygame.display.set_mode((width,length))

#setting button
button_1 = button((0,255,0),100,300,100,100,"Go")
button_2 = button((255,0,0),300,300,100,100,"Rule")
button_3 = button((255,0,0),0,100,50,50,"||")
button_4 = button((255,0,0),0,0,50,50,"R")

#setting monster
setting_1 = init_setting_2([ukiyoe_monster1, ukiyoe_monster2, ukiyoe_monster3, ukiyoe_monster4])

#setting word-type
font = pygame.font.SysFont("cochin", 20, False)
font_1 = pygame.font.SysFont("comicsans", 37, False)
press = False

#setting flags and choices
choosing_flag = False
choose = 0
choice = 0
cd_time = 0
total_score = 0
recent_count = 0
int_flag, call_flag = True, False
#start ready
scenario = senario_setting()
scenario.flag_1 = True
bg = scene[rand.randint(0,2)]

while run:

    #check the time, event of quit and pressing button
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            press = True
    pos = pygame.mouse.get_pos()

        #scene 1: main index interface
    if scenario.flag_1 == True:
        win.blit(bg,(0,0))
        text_1 = "Judging the Monsters of Ukiyoe"
        button_1.draw(win, (0,0,0))
        button_2.draw(win, (0,0,0))
        text_1 = font_1.render(text_1,0,(0,0,255))
        win.blit(text_1, (40,200))
        #press go to the game and rule to the explanation screen
        if press:
            if button_1.isOver(pos):
                scenario.flag_2 = True
                bg = scene[rand.randint(0,2)]
                scenario.flag_1 = False
                game_start_time = time.time()

            elif button_2.isOver(pos):
                scenario.flag_4 = True
                scenario.flag_1 = False
        #game over interface
    elif scenario.flag_2 == True:
    
        clock.tick(60)
        pygame.time.delay(20)
        win.blit(bg, (0,0))
        button_3.draw(win, (0,0,0))
        for i in range(0, 670, 120):
            win.blit(wall,(i - 170 , 410))
        set_same.draw(win,(0,0,0))
        set_different.draw(win,(0,0,0))

            

        if cd_time != 0:
            cd_time -= 1
            if not choosing_flag:
                win.blit(set_wrong,(400,0))
            if cd_time == 0:
                choosing_flag = False
        elif not image.start_flag:
            image.init(image.camera, image.activate)
            image.setting, image.run, image.set_clench_left ,image.set_clench_right, event, image.start_flag = image.start(image.camera, image.run, image.activate)
            if not image.run:
                run = False
            if image.activate == True and image.setting == False:
                image.cv2.destroyWindow("original")
                image.start_flag = True
            image.activate = image.setting
        else:
            image.init(image.camera, image.activate)
            image.setting, image.run, set_clench_left ,set_clench_right, event, image.start_flag = image.start(image.camera, image.run, image.activate)
            if not image.run:
                run = False
            # image.cv2.namedWindow('output_2',WINDOW_NORMAL)
            # image.cv2.namedWindow('output_1',WINDOW_NORMAL)

            if image.activate == False and image.setting == True:
                image.bgModel = None
                image.isBgCaptured = 0
                image.triggerSwitch = False
                image.cv2.destroyWindow('output_1')
                image.cv2.destroyWindow('output_2')
                image.start_flag = False
                image.reset()
                total_time = 0
                setting_1 = init_setting_2([ukiyoe_monster1, ukiyoe_monster2, ukiyoe_monster3, ukiyoe_monster4])
                correct_time, total_time = 0, 0 
                cd_time = 0
                image.start_flag = False
                back_value = []
                int_flag = True
            

                
            elif image.activate == True and image.setting == False:
                image.cv2.destroyWindow("original")
            # if event != "no event":
            #     print(event)

            else:
                if int_flag:
                    if len(back_value) < 4:
                    # it will have a chance to get a value of the first value, orelse it will return a different value
                        choice = rand.randint(0,3)
                        id = setting_1.enemy[choice].id
                    else:
                        coin = rand.randint(0,1)
                        # print(coin)
                        if coin == 0:
                            id = back_value[1]
                            choice = recent_count
                        else:
                            alist = [setting_1.enemy[i] for i in range (0,4) if setting_1.enemy[i].id is not back_value[1]]
                            choice = rand.randint(0,2)
                            id = alist[choice].id
                            for i in range (4):
                                if setting_1.enemy[i].id == id:
                                    choice = i
                                    break
                        # print(id, back_value[1])
                    back_value = insert(id, back_value)
                    recent_count = choice
                    setting_1.flag[choice] = True
                    int_flag = False
                    setting_1.enemy[choice].y = 320 
                else:
                    setting_1.enemy[choice].draw_mimic(win)
                    setting_1.enemy[choice].x -= setting_1.enemy[choice].speed / (rand.randint(1, 3) + rand.random() )
                    setting_1.enemy[choice].vanish()
                    if not setting_1.enemy[choice].show:
                        setting_1.flag[choice] = False
                
                keys = pygame.key.get_pressed()

                #character showing
                if event == "clench left":
                    call_flag = True
                    choosing_flag = True
                    set_same.color = (255,0,0)
                    set_different.color = (0,255,0)
                elif event == "clench right":
                    call_flag = False
                    choosing_flag = True
                    set_different.color = (255,0,0)
                    set_same.color = (0,255,0)
                    
                        
                if not setting_1.enemy[choice].show:
                    if call_flag == sign(back_value):
                        win.blit(set_right,(400,0))
                        correct_time += 1
                    else:
                        win.blit(set_wrong,(400,0))    
                    total_time += 1
                    int_flag = True
                    setting_1 = init_setting_2([ukiyoe_monster1, ukiyoe_monster2, ukiyoe_monster3, ukiyoe_monster4])
                    cd_time = 10   
                    set_different.color = (0,255,0)
                    set_same.color = (0,255,0)               
            

            #check crashing on monsters and give them a penalty

            texts_1 = font.render("total time: " + str(total_time),0,(255,0,0))
            win.blit(texts_1, (0,30))
            #pause for a rest
            if press:
                if button_3.isOver(pos):
                    scenario.flag_2 = False
                    scenario.flag_5 = True

            if total_time == 32:
                scenario.flag_2 = False
                scenario.flag_3 = True
            image.activate = image.setting
    elif scenario.flag_3:
        win.blit(bg,(0,0))
        correct_time /= sum_time
        fonts = pygame.font.SysFont("Comicsans", 28 , bold=True, italic=False)  
        text = fonts.render("The score you have gained:" + str(correct_time),0,(255,0,0))
        win.blit(text, (50,140))
        text = fonts.render("press retry or back to continue." ,0,(255,0,0))
        win.blit(text, (50, 240))
        button_5 = button((0,0,255),300,300,100,100,"Back")
        button_6 = button((0,255,0),100,300,100,100,"Retry")
        button_5.draw(win, (0,0,0))
        button_6.draw(win, (0,0,0))
        if press:
            if button_6.isOver(pos):
                scenario.flag_2 = True
                bg = scene[rand.randint(0,2)]
                scenario.flag_3 = False
                game_start_time = time.time()
                
            elif button_5.isOver(pos):
                scenario.flag_1 = True
                scenario.flag_3 = False
            setting_1 = init_setting_2([ukiyoe_monster1, ukiyoe_monster2, ukiyoe_monster3, ukiyoe_monster4])
            correct_time, total_time = 0, 0 
            cd_time = 0
            back_value = []
            image.bgModel = None
            image.isBgCaptured = 0
            image.triggerSwitch = False
            image.cv2.destroyWindow('output_1')
            image.cv2.destroyWindow('output_2')
            image.start_flag = False
            image.reset()
            image.start_flag = False
            int_flag = True
            
    elif scenario.flag_4:
        win.blit(bg,(0,0))
        button_4.draw(win,(0,0,0))
        fonts = pygame.font.SysFont("Comicsans", 20 , bold=True, italic=False) 
        
        text = fonts.render("Press 1 for judging the same image" ,10,(255,0,0))
        win.blit(text, (0,140))
        text = fonts.render("Press 0 for judging different" ,10,(255,0,0))
        win.blit(text, (0,210))
        text = fonts.render("The monsters will split randomly. Please judge whether" ,10,(255,0,0))
        win.blit(text, (0, 250))
        text = fonts.render("the appeared monster is the same as the three-step before" ,10,(255,0,0))
        win.blit(text, (0, 300))
        text = fonts.render("A reply will be given if you have pressed a button orelse as an error" ,10,(255,0,0))
        win.blit(text, (0, 350))
        text = fonts.render("if you do not have a reply when an image disappeared" ,10,(255,0,0))
        win.blit(text, (0, 400))

        if press:
            if button_4.isOver(pos):
                scenario.flag_4 = False
                scenario.flag_1 = True
    #pause interface
    elif scenario.flag_5:
        image.init(image.camera, image.activate)
        image.setting, image.run, set_clench_left ,set_clench_right, event, image.start_flag = image.start(image.camera, image.run, image.activate)
        if not image.run:
            run = False
        if image.activate == False and image.setting == True:
            image.bgModel = None
            image.isBgCaptured = 0
            image.triggerSwitch = False
            image.cv2.destroyWindow('output_1')
            image.cv2.destroyWindow('output_2')
        elif image.activate == True and image.setting == False:
            image.cv2.destroyWindow("original")
        if event != "no event":
            print(event)
        image.activate = image.setting

        win.blit(bg,(0,0))
        button_4.draw(win,(0,0,0))    
        fonts = pygame.font.SysFont("Arial", 30, bold=True, italic=False)  
        text = fonts.render("Game paused" ,10,(255,0,0))
        win.blit(text, (150,140))
        text = fonts.render("Press R to continue" ,10,(255,0,0))
        win.blit(text, (150,210))

        if press:
            if button_4.isOver(pos):
                scenario.flag_5 = False
                scenario.flag_2 = True

    pygame.display.update()


# while run:
    
#     image.init(image.camera, image.activate)
#     image.setting, image.run, set_clench_left ,set_clench_right, event = image.start(image.camera, image.run, image.activate)
#     if not image.run:
#         break
#     if image.activate == False and image.setting == True:
#         image.bgModel = None
#         image.isBgCaptured = 0
#         image.triggerSwitch = False
#         image.cv2.destroyWindow('output_1')
#         image.cv2.destroyWindow('output_2')
#     elif image.activate == True and image.setting == False:
#         image.cv2.destroyWindow("original")
#     if event != "no event":
#         print(event)
#     image.activate = image.setting
#     # print(activate)
  