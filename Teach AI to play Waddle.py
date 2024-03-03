#Refrences: https://realpython.com/pygame-a-primer/ , https://www.youtube.com/watch?v=jO6qQDNa2UY&list=WL&index=3&t=1130s , https://www.pygame.org/docs/ref/transform.html, https://youtu.be/WnIycS9Gf_c?si=nBcmH4enYm5tgfPT, 
#Current baby duck source: https://www.google.com/search?sca_esv=82020f27733c768a&rlz=1C1UEAD_enUS966US966&sxsrf=ACQVn0_y9kkIOCc78kcSxso8f3jzEXdsgQ:1707580113609&q=baby+duck+run&tbm=vid&source=lnms&sa=X&ved=2ahUKEwj3kePQj6GEAxVMJDQIHcAoBPgQ0pQJegQICxAB&biw=1536&bih=738&dpr=1.25#fpstate=ive&vld=cid:433d5a04,vid:CWgbmgIzoT8,st:0
#Note: used // for floor division in check_fall(self) and this works because I am using Python 3.10.11, it may change depending on your version
import pygame 
import os
import math
import time

CONSTANT_PLYR_HEIGHT = 80
CONSTANT_PLYR_WIDTH = 8*(CONSTANT_PLYR_HEIGHT//10)
CONSTANT_INITIAL_Y = 550 #To know where the floor for the duck is
CONSTANT_JUMP_SPEED = 5 #Initial speed upon jumping
screen_width = screen_height = 800 
platform_dimensions = (2*screen_width, 2*screen_height) #Don't Touch
FPS = 50
platform = pygame.Surface(platform_dimensions, pygame.SRCALPHA)
player_bounds = ((0.5*screen_width) - ((CONSTANT_INITIAL_Y - (0.5*screen_height))+CONSTANT_PLYR_HEIGHT), (0.5*screen_width) + ((CONSTANT_INITIAL_Y - (0.5*screen_height)) + CONSTANT_PLYR_HEIGHT - CONSTANT_PLYR_WIDTH)) #For player bounds to rotate platform Assuming that screen height will always be equal to screen width
baby_duck_images = [pygame.image.load(os.path.join('game images', f'duck {i}.png')) for i in range(1, 9)] #Upload all baby duck images 
space_image = pygame.transform.scale(pygame.image.load(os.path.join('game images', 'space background.png')),(screen_width, screen_height))
baby_duck_scaled = [] #empty list to be filled in for loop
for x in baby_duck_images: 
    baby_duck_scaled.append(pygame.transform.scale(x,(CONSTANT_PLYR_WIDTH, CONSTANT_PLYR_HEIGHT))) # Loop through all pictures of baby duck and scale them the same


screen = pygame.display.set_mode((screen_width, screen_height)) # Open new window for gamer
platform_color = 0 #from the list of colors which color is the platform?
rotating_platform = False #is the platform supposed to rotate?
trap_base = 0.25*screen_width
trap_height = 0.25*screen_width #Note: these are trapazoids due to perception, really but the holes are squares, trap height is the actual length of the hole
existing_holes = []
game_won = False
level_wait = 15 #Time between levels, a break for the player
hole_speed = 20 #Control the speed holes move
hole_dissapear = screen_width*0.12 #What distance from the centerpoint do the holes dissapear
hole_layer = 0
level_transition = False
platform_clockwise = True
finish_rotate = 0
platform_theta = 0
rotate_rate = 15 #When the platform rotates it's at this rate
rotate_deg = 90 / rotate_rate


hole_slots_cords = [[] for _ in range(16)]

captions = ["Now let's Waddle!", "Keep up the good work!", "Lets go!", "You're doing just okay actually, not that impressive.", "Oh look at the big fella! lets see how you handle the hard levels.", "Maybe this game isn't actually that hard. Have you thoght of that? Don't get so full of yourself."]
Levels = []

level_1 = [[False]*16 for _ in range(30)]
for i in range(30):
    for j in range(16):
        if i == 2 or i == 8:
            level_1[i][j] = True     #level_1[hole_layer][hole_number]
Levels.append(level_1)
level_2 = [[False]*16 for _ in range(30)]
for i in range(30):
    for j in range(16):
        if i % 3 == 0 or (i % 2 == 0 and j % 3 == 0):
            level_2[i][j] = True
Levels.append(level_2)
level_3 = [[False]*16 for _ in range(30)]
for i in range(30):
    for j in range(16):
        if not i == 0:
            if i % (j+1) == 0:
                level_3[i][j] = True
        else:
            level_3[i][j] = True
Levels.append(level_3)
level_4= [[False]*16 for _ in range(30)]  #False means there is no hole
level_4[0][1] = True   #True means there is a hole
Levels.append(level_4)

current_level = 1 #If =1, playing through level_1  

#*************************************************************************************************************************************************************8
def Holes_Exist(frame):
    global Levels
    global screen_width
    global hole_layer
    global level_transition
    global current_level
    global level_wait
    global game_won
    global platform_color
    if frame*hole_speed % (screen_width*0.25) == 0 and not level_transition: #if the lasthole ha moved up by one hole height then make another hole
        for hole_number in range(16):
            if Levels[current_level - 1][hole_layer][hole_number]: #Levels = [ [ [False, True, ... ], [...], [...], ...]]]
                existing_holes.append(Hole(hole_number))  
        hole_layer += 1
        if hole_layer == 30:#Check if last hole layer in level
            hole_layer = 0             
            level_transition = True
        
    elif level_transition and frame*hole_speed % (screen_width*0.25) == 0:
        hole_layer += 1
        if hole_layer == level_wait:
            hole_layer = 0
            level_transition = False
            platform_color += 1
            current_level += 1
            if current_level == len(Levels):
                game_won = True

def remove_holes():
    global existing_holes
    holes_to_delete = []
    for index in range(len(existing_holes)): #Loop through all hole objects in existing class and if too_far then ad hole object to list of holes_to_delete
        if existing_holes[index].too_far:
            holes_to_delete.append(existing_holes[index])
    for empty_rect in holes_to_delete: #Loop through list of holes_to_delete and remove them from list of existing holes
        existing_holes.remove(empty_rect)
        print("A hole has been deleted!")

class Hole(pygame.sprite.Sprite):
    def __init__(self, hole_number): # point_1 and point_2 are the width while point_3 and point_4 are the base        
        if hole_number == 0:
            self.quadrant = 1
            self.point_1 = (0.125*screen_width + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), 1.25*screen_height)
            self.point_2 = (0.125*screen_width - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), 1.25*screen_height)
            self.point_3 = (0, screen_height)
            self.point_4 = (0.25*screen_width, screen_height)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[0]+self.point_2[0])/2)) / (0.5*screen_height) ))
            self.theta = 270 - self.small_theta
            
        elif hole_number == 1:
            self.quadrant = 1
            self.point_1 = (0.375*screen_width + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), 1.25*screen_height)
            self.point_2 = (0.375*screen_width - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), 1.25*screen_height)
            self.point_3 = (0.25*screen_width, screen_height)
            self.point_4 = (0.5*screen_width, screen_height)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[0]+self.point_2[0])/2)) / (0.5*screen_height) ))
            self.theta = 270 - self.small_theta
            
        elif hole_number == 2:           
            self.quadrant = 1
            self.point_1 = (0.625*screen_width + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), 1.25*screen_height)
            self.point_2 = (0.625*screen_width - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), 1.25*screen_height)
            self.point_3 = (0.5*screen_width, screen_height)
            self.point_4 = (0.75*screen_width, screen_height)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[0]+self.point_2[0])/2)) / (0.5*screen_height) ))
            self.theta = 270 + self.small_theta
            
        elif hole_number == 3:            
            self.quadrant = 1
            self.point_1 = (0.875*screen_width + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), 1.25*screen_height)
            self.point_2 = (0.875*screen_width - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), 1.25*screen_height)
            self.point_3 = (0.75*screen_width, screen_height)
            self.point_4 = (screen_width, screen_height)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[0]+self.point_2[0])/2)) / (0.5*screen_height) ))
            self.theta = 270 + self.small_theta
            
        elif hole_number == 4:
            
            self.quadrant = 2
            self.point_1 = (1.25*screen_height, 0.875*screen_height - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_2 = (1.25*screen_height, 0.875*screen_height + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_3 = (screen_width, screen_height)
            self.point_4 = (screen_width, 0.75*screen_width)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))
            self.theta = my_degrees(-math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))
            
            
        elif hole_number == 5:            
            self.quadrant = 2
            self.point_1 = (1.25*screen_height, 0.625*screen_height - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_2 = (1.25*screen_height, 0.625*screen_height + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_3 = (screen_width, 0.75*screen_height)
            self.point_4 = (screen_width, 0.5*screen_width)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))
            self.theta = my_degrees(-math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))

        elif hole_number == 6:            
            self.quadrant = 2
            self.point_1 = (1.25*screen_height, 0.375*screen_height - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_2 = (1.25*screen_height, 0.375*screen_height + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_3 = (screen_width, 0.5*screen_height)
            self.point_4 = (screen_width, 0.25*screen_width)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))
            self.theta = self.small_theta

        elif hole_number == 7:            
            self.quadrant = 2
            self.point_1 = (1.25*screen_height, 0.125*screen_height - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_2 = (1.25*screen_height, 0.125*screen_height + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_3 = (screen_width, 0.25*screen_height)
            self.point_4 = (screen_width, 0)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))
            self.theta = self.small_theta

        elif hole_number == 8:            
            self.quadrant = 3
            self.point_1 = (0.875*screen_width - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), -0.25*screen_height)
            self.point_2 = (0.875*screen_width + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), -0.25*screen_height)
            self.point_3 = (0.75*screen_width, 0)
            self.point_4 = (screen_width, 0)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[0]+self.point_2[0])/2)) / (0.5*screen_height) ))
            self.theta = 90 - self.small_theta
            
        elif hole_number == 9:           
            self.quadrant = 3
            self.point_1 = (0.625*screen_width - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), -0.25*screen_height)           
            self.point_2 = (0.625*screen_width + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), -0.25*screen_height)
            self.point_3 = (0.5*screen_width, 0)
            self.point_4 = (0.75*screen_width, 0)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[0]+self.point_2[0])/2)) / (0.5*screen_height) ))
            self.theta = 90 - self.small_theta

        elif hole_number == 10:            
            self.quadrant = 3
            self.point_1 = (0.375*screen_width - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), -0.25*screen_height)
            self.point_2 = (0.375*screen_width + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), -0.25*screen_height)
            self.point_3 = (0.25*screen_width, 0)
            self.point_4 = (0.5*screen_width, 0)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[0]+self.point_2[0])/2)) / (0.5*screen_height) ))
            self.theta = 90 + self.small_theta
           
        elif hole_number == 11:           
            self.quadrant = 3
            self.point_1 = (0.125*screen_width - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), -0.25*screen_height) 
            self.point_2 = (0.125*screen_width + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)), -0.25*screen_height)             
            self.point_3 = (0, 0)
            self.point_4 = (0.25*screen_width, 0)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[0]+self.point_2[0])/2)) / (0.5*screen_height) ))
            self.theta = 90 + self.small_theta
                      
        elif hole_number == 12:            
            self.quadrant = 4
            self.point_1 = (-0.25*screen_height, 0.125*screen_height + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_2 = (-0.25*screen_height, 0.125*screen_height - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))            
            self.point_3 = (0, 0)
            self.point_4 = (0, 0.25*screen_height)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))
            self.theta = 180 - self.small_theta
            
        elif hole_number == 13:            
            self.quadrant = 4
            self.point_1 = (-0.25*screen_height, 0.375*screen_height + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_2 = (-0.25*screen_height, 0.375*screen_height - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))            
            self.point_3 = (0, 0.25*screen_width)
            self.point_4 = (0, 0.5*screen_height)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))
            self.theta = 180 - self.small_theta
            
        elif hole_number == 14:            
            self.quadrant = 4
            self.point_1 = (-0.25*screen_height, 0.625*screen_height + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))     
            self.point_2 = (-0.25*screen_height, 0.625*screen_height - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))            
            self.point_3 = (0, 0.5*screen_width)
            self.point_4 = (0, 0.75*screen_height)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))
            self.theta = 180 + self.small_theta
                   
        else: #hole_number is 15            
            self.quadrant = 4
            self.point_1 = (-0.25*screen_height, 0.875*screen_height + (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))
            self.point_2 = (-0.25*screen_height, 0.875*screen_height - (0.5*screen_height)*(((0.75*screen_height))/(screen_width)))            
            self.point_3 = (0, 0.75*screen_width)
            self.point_4 = (0, screen_height)
            self.small_theta = my_degrees(math.atan( abs((0.5*screen_height)-((self.point_1[1]+self.point_2[1])/2)) / (0.5*screen_height) ))
            self.theta = 180 + self.small_theta
        self.distance_iteration = 0
        self.too_far = False #if the hole is too far from the viewpoint it is deleted from the list of existing_holes
        self.possible_danger = False
        self.losing_hole = False
        self.actual_x_dist = 0
        self.hole_number = hole_number
        self.H =  (0.5*screen_height)/math.cos(inverse_my_degrees(self.small_theta))  #This is the INITIAL distance of the midpoint of the trapezoid width to the midpoint of the screen
        #print("From Hole class: created a hole with an angle of ", self.theta, " in hole spot number ", hole_number)
                 
    def __str__(self):
        return str(self.point_1, self.point_2, self.point_3, self.point_4)

    def delete_hole(self): # to delete any holes that are no longer needed
        del self

def check_danger(index, player): #this function checks to see if any of the holes intersect with certain distance from the center axis lines and marks the hole, its a square around the screen centerpoint
    global existing_holes
    global CONSTANT_INITIAL_Y
    global CONSTANT_PLYR_HEIGHT
    if player.jumping == False and not rotating_platform:
        if existing_holes[index].quadrant == 1:
            #print("hole is in quadrant 1")
            #print("The point one  y in this hole is ", existing_holes[index].point_1[1])
            #print("The point three  y in this hole is ", existing_holes[index].point_3[1])
            #print("CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT is ", (CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT))
            if (existing_holes[index].point_1[1] <= (CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT)) and (existing_holes[index].point_3[1] >= (CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT)):
                existing_holes[index].possible_danger = True
                #print("hole detected in check_danger() quadrant 1")
        elif existing_holes[index].quadrant == 2:
            #print("hole is in quadrant 2")
            if existing_holes[index].point_1[0] <= (CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT) and existing_holes[index].point_3[0] >= (CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT):
                existing_holes[index].possible_danger = True
                #print("hole detected in check_danger() quadrant 2")
        elif existing_holes[index].quadrant == 3:
            #print("hole is in quadrant 3")
            if existing_holes[index].point_1[1] >= (screen_height - (CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT)) and existing_holes[index].point_3[1] <= (screen_height - (CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT)):
                existing_holes[index].possible_danger = True
                #print("hole detected in check_danger() quadrant 2")
        else: # if quadrant 4
            #print("hole is in quadrant 4")
            if existing_holes[index].point_1[0] >= (screen_height - (CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT)) and existing_holes[index].point_3[0] <= (screen_height - (CONSTANT_INITIAL_Y + CONSTANT_PLYR_HEIGHT)):
                existing_holes[index].possible_danger = True
                #print("hole detected in check_danger() quadrant 2")
        #print("Used check_danger()")

def draw_screen(duck_step, BabyDuck1, frame):
    BabyDuck1.check_fall()
    if not BabyDuck1.game_over:
        pygame.display.set_caption("Now let's WADDLE!")
    else:
        pygame.display.set_caption("Game Over. You Lose")
    BabyDuck1.check_walls()
    screen.blit(space_image, (0, 0)) # Fill the background with space image resized
    draw_holes(frame, BabyDuck1)
    BabyDuck1.draw_duck(duck_step) #Draw duck ontop of space image
    pygame.display.update()

def draw_holes(frame, BabyDuck1): #Draws holes on platform #trap_vertices will be a list of lists of coordinates like [[(coordinates),(...),(...),(...)],[(...),(...),(...),(...)],[(...),(...),(...),(...)]]      
    # Create a trapezoidal mask (transparent surface)
    global existing_holes 
    global platform_dimensions        
    pygame.draw.rect(platform, plat_color(), (0.5 * screen_width - 0.5 * platform_dimensions[0], 0.5 * screen_height - 0.5 * platform_dimensions[1], 1.15*platform_dimensions[0], 1.15*platform_dimensions[1])) # Create a colored platform
    hole = pygame.Surface((platform_dimensions[0], platform_dimensions[1]), pygame.SRCALPHA)
    square_cut = [adjust_plat_loc(screen_width*0.45, screen_height*0.45), 
                 adjust_plat_loc(screen_width*0.45, screen_height*0.55), 
                 adjust_plat_loc(screen_width*0.55, screen_height*0.55), 
                 adjust_plat_loc(screen_width*0.55, screen_height*0.45)] #Space at the end of the tunnel
    pygame.draw.polygon(hole, (0, 0, 0, 255), square_cut)  
     
    for index in range(len(existing_holes)): #For every trapazoid in the list of existing_holes cut the hole into the platform
        trap = move_holes(index, frame) #Update the hole location
        check_danger(index, BabyDuck1) #Check if hole could possibly make player fail
        #print("From draw_holes() the existing_holes[index].actual_x_dist after updating the hole is ", existing_holes[index].actual_x_dist)
        
        if not (trap == [(),(),(),()]):  
            existing_holes[index].point_1 = trap[0]
            existing_holes[index].point_2 = trap[1]
            existing_holes[index].point_3 = trap[2]
            existing_holes[index].point_4 = trap[3]
            #print("The cordinates of trap are: P1=", trap[0], ", P2=", trap[1], ", P3=", trap[2], ", P4=", trap[3])
            updated_trap = []
            updated_trap = [adjust_plat_loc(trap[i][0], trap[i][1]) for i in range(4)]
            #print("The cordinates of trap after updating the points are are: P1=", updated_trap[0], ", P2=", updated_trap[1], ", P3=", updated_trap[2], ", P4=", updated_trap[3])
            pygame.draw.polygon(hole, (0, 0, 0, 255), updated_trap) 
        else:
            print(" trap == [(),(),(),()] ")  
    remove_holes()     
            
    platform.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_SUB) #Draw hole on platform surface
    rotated_platform, center = turn_platform()
    screen.blit(rotated_platform, center) #Draw new platform

def plat_color():
    global platform_color
    platt_color = [(0, 0, 128),    # Oceanic_blue
                   (64, 224, 208), # Turquoise
                   (0, 255, 255),  # Cyan
                   (255, 0, 0),    # Red
                   (255, 165, 0),  # Orange
                   (255, 255, 0),  # Yellow
                   (0, 255, 0),    # Green
                   (0, 0, 255),    # Blue
                   (0, 128, 0) ,   # Grassy green
                   (102, 51, 153), # Rebecca Purple
                   (127, 255, 212),# Aquamarine
                   (240, 230, 140),# Khaki
                   (255, 215, 0),  # Gold
                   (255, 192, 203),# Pink
                   (128, 128, 0),  # Olive
                   (255, 239, 213),# Papaya Whip
                   (255, 0, 255),  # Fuchsia
                   (220, 220, 220),# Gainsboro
                   (75, 0, 130),   # Indigo
                   (128, 0, 128)  ]# Purple
    index = platform_color % len(platt_color)
    return platt_color[index]

def move_holes(index, frame):
    global FPS
    global hole_slots_cords
    point_1, point_2, point_3, point_4 = (), (), (), ()
    if not rotating_platform: #check if platform is rotating to stop hole motion
        point_1 = hole_slots_cords[existing_holes[index].hole_number][existing_holes[index].distance_iteration][0]
        #print("Point 1 cordinates are ", point_1, " from quadrant ", existing_holes[index].quadrant)
        point_2 = hole_slots_cords[existing_holes[index].hole_number][existing_holes[index].distance_iteration][1]
        #print("Point 2 cordinates are ", point_2, " from quadrant ", existing_holes[index].quadrant)
        point_3 = hole_slots_cords[existing_holes[index].hole_number][existing_holes[index].distance_iteration][2]
        #print("Point 3 cordinates are ", point_3, " from quadrant ", existing_holes[index].quadrant)
        point_4 = hole_slots_cords[existing_holes[index].hole_number][existing_holes[index].distance_iteration][3]
        #print("Point 4 cordinates are ", point_4, " from quadrant ", existing_holes[index].quadrant)
        #print()        
        existing_holes[index].distance_iteration += 1
        if existing_holes[index].distance_iteration == len(hole_slots_cords[existing_holes[index].hole_number]):
            existing_holes[index].too_far = True
        
        
    else:   
        point_1 = existing_holes[index].point_1
        point_2 = existing_holes[index].point_2
        point_3 = existing_holes[index].point_3
        point_4 = existing_holes[index].point_4

    updated_trap_points = [point_1, point_2, point_3, point_4] # actual resulting points
    return updated_trap_points

def adjust_plat_loc(x, y):
    new_vec = (x+0.25*platform_dimensions[0], y+0.25*platform_dimensions[1])
    return new_vec

def find_trap_points(cordinate_2_base, trap_percieved_base, cordinate_2_width, trap_percieved_width, index):
    # The quadrant system and point system in use:
    #    \ 3 /
    #     \ /       
    #   4  x  2     P3---P4
    #     / \      /       \
    #    / 1 \   P2---------P1
    quadrant = existing_holes[index].quadrant
    if quadrant == 1:        
        point_1 = ((cordinate_2_base[0]  + 0.5*trap_percieved_base) + (0.5*screen_width),  (-cordinate_2_base[1] + (0.5*screen_width)))
        point_2 = ((cordinate_2_base[0]  - 0.5*trap_percieved_base) + (0.5*screen_width),  (-cordinate_2_base[1] + (0.5*screen_width)))    
        point_3 = ((cordinate_2_width[0] - 0.5*trap_percieved_width) + (0.5*screen_width), (-cordinate_2_width[1] + (0.5*screen_width)))
        point_4 = ((cordinate_2_width[0] + 0.5*trap_percieved_width) + (0.5*screen_width), (-cordinate_2_width[1] + (0.5*screen_width)))
        #print("The previous cordinates of the hole were: P1=", existing_holes[index].point_1,", P2=", existing_holes[index].point_2, ", P3=", existing_holes[index].point_3, ", P4=", existing_holes[index].point_4, " in quadrant ", quadrant)
        #print("  The updated cordinates of the hole are: P1=", point_1, ", P2=", point_2, ", P3=", point_3, ", P4=", point_4)
        if (-cordinate_2_width[1]) <= hole_dissapear:
                point_1, point_2, point_3, point_4 = (), (), (), ()
                existing_holes[index].too_far = True  #Hole will be deleted soon
    if quadrant == 2:                    
        point_1 = ((cordinate_2_base[0] + (0.5*screen_width)) ,  (-cordinate_2_base[1]  - 0.5*trap_percieved_base) + (0.5*screen_width)) 
        point_2 = ((cordinate_2_base[0] + (0.5*screen_width)) ,  (-cordinate_2_base[1]  + 0.5*trap_percieved_base) + (0.5*screen_width)) 
        point_3 = ((cordinate_2_width[0] + (0.5*screen_width)) ,  (-cordinate_2_width[1] + 0.5*trap_percieved_width) + (0.5*screen_width))
        point_4 = ((cordinate_2_width[0] + (0.5*screen_width)) ,  (-cordinate_2_width[1] - 0.5*trap_percieved_width) + (0.5*screen_width))
        if (cordinate_2_width[0]) <= hole_dissapear:
            point_1, point_2, point_3, point_4 = (), (), (), ()
            existing_holes[index].too_far = True  #Hole will be deleted soon                  
    elif quadrant == 3:
        point_1 = ((cordinate_2_base[0]  - 0.5*trap_percieved_base) + (0.5*screen_width),   (-cordinate_2_base[1] + (0.5*screen_width)))
        point_2 = ((cordinate_2_base[0]  + 0.5*trap_percieved_base) + (0.5*screen_width),   (-cordinate_2_base[1] + (0.5*screen_width)))                    
        point_3 = ((cordinate_2_width[0] + 0.5*trap_percieved_width) + (0.5*screen_width),  (-cordinate_2_width[1] + (0.5*screen_width)))    
        point_4 = ((cordinate_2_width[0] - 0.5*trap_percieved_width) + (0.5*screen_width),  (-cordinate_2_width[1] + (0.5*screen_width))) 
        if (cordinate_2_width[1]) <= hole_dissapear:
            point_1, point_2, point_3, point_4 = (), (), (), ()
            existing_holes[index].too_far = True  #Hole will be deleted soon                   
    elif quadrant == 4:          
        point_1 = ((cordinate_2_base[0] + (0.5*screen_width)),  (-cordinate_2_base[1] + 0.5*trap_percieved_base) + (0.5*screen_width))
        point_2 = ((cordinate_2_base[0] + (0.5*screen_width)),  (-cordinate_2_base[1] - 0.5*trap_percieved_base) + (0.5*screen_width))
        point_3 = ((cordinate_2_width[0] + (0.5*screen_width)),  (-cordinate_2_width[1]  - 0.5*trap_percieved_width) + (0.5*screen_width))    
        point_4 = ((cordinate_2_width[0] + (0.5*screen_width)),  (-cordinate_2_width[1]  + 0.5*trap_percieved_width) + (0.5*screen_width))  
        if (-cordinate_2_width[0]) <= hole_dissapear:
                point_1, point_2, point_3, point_4 = (), (), (), ()
                existing_holes[index].too_far = True  #Hole will be deleted soon
    
    return point_1, point_2, point_3, point_4


def init_hole_distances():
    global hole_slots_cords   
    global hole_dissapear
    global hole_speed
    slots_width_mid_cord = [[] for _ in range(16)]
    slots_base_mid_cord = [[] for _ in range(16)]
       
    start_time = time.time()
    for hole_num in range(16):
        hole = Hole(hole_num)   
        move_hole_more = True     
        while move_hole_more: 
            new_zeta = my_degrees(math.atan2( (hole.actual_x_dist), hole.H )) 
            viewed_dist_2 = (new_zeta*(math.pi*hole.H))/360
            cordinate_2_width = ((hole.H-viewed_dist_2)*math.cos(inverse_my_degrees(hole.theta))), ((hole.H-viewed_dist_2)*(math.sin(inverse_my_degrees(hole.theta))))
            slots_width_mid_cord[hole_num].append(cordinate_2_width)#The new cordinate for the width is inserted
            new_zeta = my_degrees(math.atan2(hole.actual_x_dist + (0.25*screen_width), hole.H)) 
            viewed_dist_2 = (new_zeta*(math.pi*hole.H))/360
            cordinate_2_base = ((hole.H-viewed_dist_2)*math.cos(inverse_my_degrees(hole.theta))), ((hole.H-viewed_dist_2)*(math.sin(inverse_my_degrees(hole.theta))))
            slots_base_mid_cord[hole_num].append(cordinate_2_base)#The new cordinate for the base is inserted
            hole_slots_cords[hole_num].append([])
            hole.actual_x_dist += hole_speed            
            if hole.quadrant == 1:
                #print("From init_hole_distances() this is quadrant 1")
                #print("Hole disspear is ", hole_dissapear, " y cordinate of width is ", -cordinate_2_width[1])
                if (-cordinate_2_width[1]) <= hole_dissapear:
                    move_hole_more = False                
                    #print("Finished with moving hole slot ", hole_num, " from quadrant ", hole.quadrant)
            elif hole.quadrant == 2:
                if (cordinate_2_width[0]) <= hole_dissapear:
                    move_hole_more = False
                    #print("Finished with moving hole slot ", hole_num, " from quadrant ", hole.quadrant)
            elif hole.quadrant == 3:
                if (cordinate_2_width[1]) <= hole_dissapear:
                    move_hole_more = False
                    #print("Finished with moving hole slot ", hole_num, " from quadrant ", hole.quadrant)
            else: #quadrant 4
                if (-cordinate_2_width[0]) <= hole_dissapear:
                    move_hole_more = False 
                    #print("Finished with moving hole slot ", hole_num, " from quadrant ", hole.quadrant)
        
        for index in range(len(slots_base_mid_cord[hole_num])):
            if hole.quadrant == 1 or hole.quadrant == 3:
                trap_percieved_base = (0.25 * screen_width) * (abs(slots_base_mid_cord[hole_num][index][1]) / (0.5*screen_width)) #control size of trapezoid base
                trap_percieved_width = (0.25 * screen_width) * (abs(slots_width_mid_cord[hole_num][index][1]) / (0.5*screen_width))  #control size of trapezoid width
            else: #If quadrant is 2 or 4            
                trap_percieved_base = (0.25 * screen_width) * (abs(slots_base_mid_cord[hole_num][index][0]) / (0.5*screen_width)) #control size of trapezoid base 
                trap_percieved_width = (0.25 * screen_width) * (abs(slots_width_mid_cord[hole_num][index][0]) / (0.5*screen_width)) #control size of trapezoid width
            if hole.quadrant == 1:        
                point_1 = ((slots_base_mid_cord[hole_num][index][0]  + 0.5*trap_percieved_base) + (0.5*screen_width),  (-slots_base_mid_cord[hole_num][index][1] + (0.5*screen_width)))
                point_2 = ((slots_base_mid_cord[hole_num][index][0]  - 0.5*trap_percieved_base) + (0.5*screen_width),  (-slots_base_mid_cord[hole_num][index][1] + (0.5*screen_width)))    
                point_3 = ((slots_width_mid_cord[hole_num][index][0] - 0.5*trap_percieved_width) + (0.5*screen_width), (-slots_width_mid_cord[hole_num][index][1] + (0.5*screen_width)))
                point_4 = ((slots_width_mid_cord[hole_num][index][0] + 0.5*trap_percieved_width) + (0.5*screen_width), (-slots_width_mid_cord[hole_num][index][1] + (0.5*screen_width)))               
            elif hole.quadrant == 2:                    
                point_1 = ((slots_base_mid_cord[hole_num][index][0] + (0.5*screen_width)) ,  (-slots_base_mid_cord[hole_num][index][1]  - 0.5*trap_percieved_base) + (0.5*screen_width)) 
                point_2 = ((slots_base_mid_cord[hole_num][index][0] + (0.5*screen_width)) ,  (-slots_base_mid_cord[hole_num][index][1]  + 0.5*trap_percieved_base) + (0.5*screen_width)) 
                point_3 = ((slots_width_mid_cord[hole_num][index][0] + (0.5*screen_width)) ,  (-slots_width_mid_cord[hole_num][index][1] + 0.5*trap_percieved_width) + (0.5*screen_width))
                point_4 = ((slots_width_mid_cord[hole_num][index][0] + (0.5*screen_width)) ,  (-slots_width_mid_cord[hole_num][index][1] - 0.5*trap_percieved_width) + (0.5*screen_width))                                     
            elif hole.quadrant == 3:
                point_1 = ((slots_base_mid_cord[hole_num][index][0]  - 0.5*trap_percieved_base) + (0.5*screen_width),   (-slots_base_mid_cord[hole_num][index][1] + (0.5*screen_width)))
                point_2 = ((slots_base_mid_cord[hole_num][index][0]  + 0.5*trap_percieved_base) + (0.5*screen_width),   (-slots_base_mid_cord[hole_num][index][1] + (0.5*screen_width)))                    
                point_3 = ((slots_width_mid_cord[hole_num][index][0] + 0.5*trap_percieved_width) + (0.5*screen_width),  (-slots_width_mid_cord[hole_num][index][1] + (0.5*screen_width)))    
                point_4 = ((slots_width_mid_cord[hole_num][index][0] - 0.5*trap_percieved_width) + (0.5*screen_width),  (-slots_width_mid_cord[hole_num][index][1] + (0.5*screen_width)))                                       
            else: #hole quadrant is quadrant 4     
                point_1 = ((slots_base_mid_cord[hole_num][index][0] + (0.5*screen_width)),  (-slots_base_mid_cord[hole_num][index][1] + 0.5*trap_percieved_base) + (0.5*screen_width))
                point_2 = ((slots_base_mid_cord[hole_num][index][0] + (0.5*screen_width)),  (-slots_base_mid_cord[hole_num][index][1] - 0.5*trap_percieved_base) + (0.5*screen_width))
                point_3 = ((slots_width_mid_cord[hole_num][index][0] + (0.5*screen_width)),  (-slots_width_mid_cord[hole_num][index][1]  - 0.5*trap_percieved_width) + (0.5*screen_width))    
                point_4 = ((slots_width_mid_cord[hole_num][index][0] + (0.5*screen_width)),  (-slots_width_mid_cord[hole_num][index][1]  + 0.5*trap_percieved_width) + (0.5*screen_width))  
            hole_slots_cords[hole_num][index].append(point_1)
            hole_slots_cords[hole_num][index].append(point_2)
            hole_slots_cords[hole_num][index].append(point_3)
            hole_slots_cords[hole_num][index].append(point_4)
    #print("The final hole_slots_cords is ", hole_slots_cords)        
    end_time = time.time()
    print("All possible hole cordinates have been calculated and it took ", (end_time - start_time), " seconds.")

def my_degrees(rad):
    rad = math.degrees(rad)
    if rad < 0:
        rad += 360
    return rad

def inverse_my_degrees(degree):
    if degree > 180:
        degree -=  360
    return math.radians(degree)

def turn_platform():
    global rotating_platform
    global platform_theta  
    global finish_rotate
    global rotate_deg
    if rotating_platform and platform_clockwise:
        platform_theta -= rotate_deg
        finish_rotate += rotate_deg
        if finish_rotate == 90:
            rotating_platform = False
            finish_rotate = 0
        
    elif rotating_platform and not platform_clockwise:
        platform_theta += rotate_deg #rate at which platform rotates
        finish_rotate += rotate_deg
        if finish_rotate == 90:
            rotating_platform = False
            finish_rotate = 0

    rotated_platform = pygame.transform.rotate(platform, platform_theta) #Save new rotated platform
    center = rotated_platform.get_rect(center=(0.5 * screen_width, 0.5 * screen_height)) 
    return rotated_platform, center

# Define a Player object by extending pygame.sprite.Sprite
class Player(pygame.sprite.Sprite):

    def __init__(self):        
        self.x_pos = screen_width/2
        self.y_pos = CONSTANT_INITIAL_Y
        self.delta_y = float(CONSTANT_JUMP_SPEED) #Up/down Velocity
        self.rotat_delt_x = 0
        self.rotat_delt_y = 0
        self.jumping = False
        self.left = False
        self.right = False
        self.duck_slide = 3 #How fast duck moves left or right
        self.draw_duck(0) #The 0 is for duck_step
        self.game_over = False

    def draw_duck(self, duck_step):
        global rotate_rate
        global platform_clockwise
        if  rotating_platform:
            self.left = False
            self.right = False            
            self.x_pos += self.rotat_delt_x
            self.y_pos += self.rotat_delt_y
            screen.blit(baby_duck_scaled[0], (self.x_pos, self.y_pos)) 
            
        else:
            if self.left:
                self.x_pos -= self.duck_slide
                self.left = False
            if self.right:
                self.x_pos += self.duck_slide
                self.right = False           
            if not self.jumping:
                self.run(duck_step)
            else:
                self.jump(duck_step)
    
    def check_walls(self):
        global player_bounds
        global rotating_platform
        global platform_clockwise
        global rotate_rate
        global CONSTANT_INITIAL_Y
        global CONSTANT_PLYR_WIDTH
        if not rotating_platform:
            if self.x_pos < player_bounds[0]:
                rotating_platform = True
                platform_clockwise = False
                self.jumping = False
                self.delta_y = 0
                self.rotat_delt_x = ((player_bounds[1] - (self.x_pos)) - (CONSTANT_INITIAL_Y - self.y_pos)) / rotate_rate #move duck right when rotating platform counterclockwise
                self.rotat_delt_y = (CONSTANT_INITIAL_Y - self.y_pos) / rotate_rate
            elif self.x_pos > player_bounds[1]:
                rotating_platform = True
                platform_clockwise = True
                self.jumping = False
                self.delta_y = CONSTANT_JUMP_SPEED
                self.rotat_delt_x = ((player_bounds[0] - self.x_pos) + (CONSTANT_INITIAL_Y - self.y_pos)) / rotate_rate #move duck left when rotating platform clockwise
                self.rotat_delt_y = (CONSTANT_INITIAL_Y - self.y_pos) / rotate_rate

    def check_fall(self):
        global existing_holes
        global platform_theta
        global rotating_platform
        global player_bounds
        global CONSTANT_PLYR_WIDTH
        #print("check_fall() function is in use")        
        if self.jumping == False and not rotating_platform:
            duck_hole_slot = (self.x_pos + (0.5 * CONSTANT_PLYR_WIDTH) - player_bounds[0]) // (((0.5 * CONSTANT_PLYR_WIDTH) + player_bounds[1] - player_bounds[0]) / 4) #If 1 2 3 4 then 0 will be slot 1 for hole slots
            for hole in existing_holes: #loop through all existing holes to see which ones could be a threat
                if hole.possible_danger:
                    if platform_theta < 0:
                        if hole.quadrant == (platform_theta % 360)/90: #Check if hole is in the same platform as the duck
                            if (hole.hole_number % 4) == duck_hole_slot: #Check if the Duck is in the same hole slot as the dangerous hole
                                self.game_over = True
                                hole.losing_hole = True
                                print("You lost to a hole in quadrant ", hole.quadrant, " and in hole slot ", hole.hole_number)

                    else: #if total platform rotation was positive and counter clockwise
                        if hole.quadrant == 1 and platform_theta % 360 == 0:
                            if (hole.hole_number % 4) == duck_hole_slot: #Check if the Duck is in the same hole slot as the dangerous hole
                                self.game_over = True
                                hole.losing_hole = True
                                print("You lost to a hole in quadrant ", hole.quadrant, " and in hole slot ", hole.hole_number)

                        elif hole.quadrant == 4 and platform_theta % 360 == 90:
                            if (hole.hole_number % 4) == duck_hole_slot: #Check if the Duck is in the same hole slot as the dangerous hole
                                self.game_over = True
                                hole.losing_hole = True
                                print("You lost to a hole in quadrant ", hole.quadrant, " and in hole slot ", hole.hole_number)

                        elif hole.quadrant == 3 and platform_theta % 360 == 180:
                            if (hole.hole_number % 4) == duck_hole_slot: #Check if the Duck is in the same hole slot as the dangerous hole
                                self.game_over = True
                                hole.losing_hole = True
                                print("You lost to a hole in quadrant ", hole.quadrant, " and in hole slot ", hole.hole_number)

                        elif hole.quadrant == 2 and platform_theta % 360 == 270:
                            if (hole.hole_number % 4) == duck_hole_slot: #Check if the Duck is in the same hole slot as the dangerous hole
                                self.game_over = True
                                hole.losing_hole = True
                                print("You lost to a hole in quadrant ", hole.quadrant, " and in hole slot ", hole.hole_number)

            if not self.game_over:
                for hole in existing_holes:
                    hole.possible_danger = False
            
    def run(self, duck_step):
        if duck_step % 8 == 0:
            screen.blit(baby_duck_scaled[7], (self.x_pos, self.y_pos))
        elif duck_step % 8 == 1:
            screen.blit(baby_duck_scaled[6], (self.x_pos, self.y_pos))
        elif duck_step % 8 == 2:
            screen.blit(baby_duck_scaled[5], (self.x_pos, self.y_pos))
        elif duck_step % 8 == 3:
            screen.blit(baby_duck_scaled[4], (self.x_pos, self.y_pos))
        elif duck_step % 8 == 4:
            screen.blit(baby_duck_scaled[3], (self.x_pos, self.y_pos))
        elif duck_step % 8 == 5:
            screen.blit(baby_duck_scaled[2], (self.x_pos, self.y_pos))
        elif duck_step % 8 == 6:
            screen.blit(baby_duck_scaled[1], (self.x_pos, self.y_pos))
        else:
            screen.blit(baby_duck_scaled[0], (self.x_pos, self.y_pos))

    def jump(self, duck_step):
        self.y_pos -= int(self.delta_y)
        self.delta_y = self.delta_y - (2/FPS*CONSTANT_JUMP_SPEED)
        if self.y_pos > CONSTANT_INITIAL_Y: #If player lands at initial height stop falling
            self.y_pos = CONSTANT_INITIAL_Y
            self.jumping = False
            self.delta_y = CONSTANT_JUMP_SPEED
        screen.blit(baby_duck_scaled[0], (self.x_pos, self.y_pos)) #Put jumping duck image on top of background

def Loss(baby_duck,  all_hole, ledge_x, clock):
    global FPS
    loss_length = 10 #How long the loss scene will last in seconds
    print("   |   |  | |  ")
    print("       |       ")
    print("-------+-------")
    print("       |       ")
    print(" | |   |  | __ ")
    print("  ")
    print("  ")
    finished = False
    frame = 1
    while not finished:
        clock.tick(FPS) # Stop updating until time of 1/FPS passes
        frame += 1
        if frame / FPS == loss_length:
            finished = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Did the user click the window close button?
                    finished = True
        draw_losing_frames(baby_duck, all_hole, ledge_x)
        
def draw_losing_frames(baby_duck, all_hole, ledge_x):
    global existing_holes 
    global platform_dimensions        
    pygame.draw.rect(platform, plat_color(), (0.5 * screen_width - 0.5 * platform_dimensions[0], 0.5 * screen_height - 0.5 * platform_dimensions[1], 1.15*platform_dimensions[0], 1.15*platform_dimensions[1])) # Create a colored platform
    hole = pygame.Surface((platform_dimensions[0], platform_dimensions[1]), pygame.SRCALPHA)
    square_cut = [adjust_plat_loc(screen_width*0.45, screen_height*0.45), 
                 adjust_plat_loc(screen_width*0.45, screen_height*0.55), 
                 adjust_plat_loc(screen_width*0.55, screen_height*0.55), 
                 adjust_plat_loc(screen_width*0.55, screen_height*0.45)] #Space at the end of the tunnel
    pygame.draw.polygon(hole, (0, 0, 0, 255), square_cut)  

def no_or_partial_ground(BabyDuck1): #function returns first if player base was partly on ground or not and then returns an x value for where the ledge was 
    global existing_holes
    global player_bounds
    global CONSTANT_PLYR_WIDTH
    
    count = 0
    for hole in existing_holes:
        if hole.losing_hole:
            count += 1 
        if count == 2:
            return True
        if hole.hole_number % 4 == 0: #left most hole slot
            if (BabyDuck1.x_pos >= player_bounds[0]) and ((BabyDuck1.x_pos + CONSTANT_PLYR_WIDTH ) < (((player_bounds[1] + CONSTANT_PLYR_WIDTH - player_bounds[0]) / 4) + player_bounds[0])):
                return True, 0
            
        elif hole.hole_number % 4 == 1: #second to left hole slot
            if ((BabyDuck1.x_pos) > (((player_bounds[1] + CONSTANT_PLYR_WIDTH - player_bounds[0]) / 4) + player_bounds[0])) and ((BabyDuck1.x_pos + CONSTANT_PLYR_WIDTH ) < ((((player_bounds[1] + CONSTANT_PLYR_WIDTH - player_bounds[0]) / 4) * 2) + player_bounds[0])):
                return True, 0
        elif hole.hole_number % 4 == 2: #second to right hole slot
            if  ((BabyDuck1.x_pos) > ((((player_bounds[1] + CONSTANT_PLYR_WIDTH - player_bounds[0]) / 4) * 2) + player_bounds[0])) and  ((BabyDuck1.x_pos + CONSTANT_PLYR_WIDTH ) < ((((player_bounds[1] + CONSTANT_PLYR_WIDTH - player_bounds[0]) / 4) * 3) + player_bounds[0])):
                return True, 0
        else: #right most hole slot
            if ((BabyDuck1.x_pos) > ((((player_bounds[1] + CONSTANT_PLYR_WIDTH - player_bounds[0]) / 4) * 3) + player_bounds[0])) and (BabyDuck1.x_pos <= player_bounds[1]):
                return True, 0      
    ledge_x = (round(((0.5*CONSTANT_PLYR_WIDTH) + BabyDuck1.x_pos) / ((player_bounds[1] + CONSTANT_PLYR_WIDTH - player_bounds[0]) / 4)) * ((player_bounds[1] + CONSTANT_PLYR_WIDTH - player_bounds[0]) / 4)) + player_bounds[0] #The ledge x cordinate
    return False, ledge_x

def main():   
    global rotating_platform    
    global platform_clockwise   
    global game_won
    init_hole_distances()
    close_window = False # Did the user try to close the gaming window
    BabyDuck1 = Player()
    slow_duck = 5 # factor to slow duck waddle down by (5 looks good)
    duck_step = 0
    frame = 0
    clock = pygame.time.Clock()   
    
    while not close_window: # Keep gaming window open for our gamer
        clock.tick(FPS) # Stop updating until time of 1/FPS passes
        
        
        if frame % slow_duck == 0: #reduce frequency of duck steps
            duck_step += 1

        keys_pressed = pygame.key.get_pressed() #put all pressed keys in this list of true and false values
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Did the user click the window close button?
                close_window = True
        if keys_pressed[pygame.K_s]:
            time.sleep(4)#Sleep for 4 seconds when the space bar is pushed
        
        if keys_pressed[pygame.K_SPACE]:
            BabyDuck1.jumping = True
        if keys_pressed[pygame.K_LEFT]:
            BabyDuck1.left = True
        if keys_pressed[pygame.K_RIGHT]:
            BabyDuck1.right = True
        if BabyDuck1.left and BabyDuck1.right:
            BabyDuck1.left = False
            BabyDuck1.right = False
        
        if not rotating_platform: #Check if platform is rotating and stop hole motion besides rotation
            frame += 1 
        if not BabyDuck1.game_over:
            Holes_Exist(frame)
            draw_screen(duck_step, BabyDuck1,frame )
        elif BabyDuck1.game_over:#Game over lose transition
            all_hole, ledge_x = no_or_partial_ground(BabyDuck1)
            Loss(BabyDuck1, all_hole, ledge_x, clock) 
            close_window = True

        elif game_won and not BabyDuck1.game_over:
            pass


    pygame.quit() # User closed window Time to quit.

if __name__ == "__main__":
    main()
