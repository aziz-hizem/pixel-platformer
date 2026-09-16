import pygame 
import os
import random
import time
from os import listdir
from os.path import isfile, join

# Load assets relative to this file, whatever folder the game is started from
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
pygame.display.set_caption("Hizem's Game")

# Background music is optional: loop the first mp3 found in music/ (not part of the repository)
music_files = sorted(f for f in listdir("music") if f.lower().endswith(".mp3")) if os.path.isdir("music") else []
if music_files:
    pygame.mixer.music.load(join("music", music_files[0]))
    pygame.mixer.music.play(-1)


WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 6

window = pygame.display.set_mode((WIDTH,HEIGHT))

def draw_text(window, x, y, text, font, color, size, duration):
    start_time = time.time()
    font = pygame.font.SysFont(font, size)  
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.x, text_rect.y = x, y
    #window.blit(text_surface, text_rect)
    
    # Main loop for drawing the text
    while time.time() - start_time < duration:
        window.blit(text_surface, text_rect)
        pygame.display.update()
        #pygame.time.delay(10)  # Slight delay to prevent CPU overload

def flip (sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_yajour(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96*3-16, 64, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player (pygame.sprite.Sprite):

    COLOR = (255,0,0)
    GRAVITY = 1
    CHARACTER_CHANGE = 0
    ANIMATION_DELAY = 3
    char_list =["MaskDude", "NinjaFrog", "PinkMan", "VirtualGuy"]
    SPRITES = load_sprite_sheets("MainCharacters", random.choice(char_list),32,32,True)
    HIT_COOLDOWN = 2 

    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y, width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.lives_count = 4
        self.last_hit_time = 0  # Time when the player was last hit
        self.sprite = self.SPRITES["idle_right"][0] 
    
    def jump(self):
        self.y_vel = -self.GRAVITY * 10 
        self.animation_count = 0
        self.jump_count += 1 
        if self.jump_count == 1:
            self.fall_count = 0

    def move (self,dx,dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self, can_hit):
        if can_hit and self.can_be_hit():
            self.hit = True
            self.hit_count = 0
            self.lives_count -= 1
            self.last_hit_time = time.time()  # Update the last hit time
            #self.rect.x -= 40

    def can_be_hit(self):
        return time.time() - self.last_hit_time >= self.HIT_COOLDOWN    
        
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right (self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop (self, fps):
        self.y_vel += min(1, (self.fall_count / fps ) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit :
            self.hit_count += 1 
        if self.hit_count > fps* 1.5 : # fps* 1.5 = 1.5 seconds
            self.hit = False
            self.hit_count = 0


        self.fall_count += 1 
        self.update_sprite()
    
    def landed (self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head (self) : 
        self.count = 0 
        self.y_vel *=-1

    def update_sprite (self):
        sprite_sheet = "idle"
        if self.hit :
            sprite_sheet = "hit" 
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet ="double_jump"
        elif self.y_vel > self.GRAVITY * 2 :
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1 
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object (pygame.sprite.Sprite):
    def __init__(self,x,y,width,height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width,height),pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__ (self,x,y, size):
        super().__init__(x,y,size,size)
        block = get_block(size)
        self.image.blit (block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Yajour (Object) :
    def __init__ (self,x,y,size):
        super().__init__(x,y,size,size)
        block = get_yajour(size)
        self.image.blit (block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire (Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets ("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count =  0
        self.animation_name = "off"
    
    def on (self):
        self.animation_name = "on"
    
    def off(self):
        self.animation_name ="off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1 
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Info(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self, win, offset_x=0):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Button (pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, idle_path, click_path):
        super().__init__()
        self.idle = pygame.image.load(idle_path).convert_alpha()
        self.click = pygame.image.load(click_path).convert_alpha()

        self.image = pygame.transform.scale(self.idle, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.clicked = False
        self.click_time = 0
        self.click_duration = 0.1

    def draw(self, win):
        win.blit(self.image, (self.rect.x , self.rect.y))
        if self.clicked and time.time() - self.click_time > self.click_duration:
            self.clicked = False
            self.image = pygame.transform.scale(self.idle, self.rect.size)

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            if not self.clicked:
                self.clicked = True
                self.click_time = time.time()
                self.image = pygame.transform.scale(self.click, self.rect.size)  # Change to clicked image
            return True
        return False

class Lives (pygame.sprite.Sprite):

    def __init__(self, x, y, width, height, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, win):
        win.blit(self.image, (self.rect.x , self.rect.y))

class Menu (pygame.sprite.Sprite): 
    def __init__(self, x, y, width, height, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self, win, x_pos):
        win.blit(self.image, (x_pos, self.rect.y))

def get_background(name):
    image = pygame.image.load(join("assets","Background",name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width +1):
        for j in range (HEIGHT // height +1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, pause, background, bg_image, player, objects, lives, keyboard, fire_danger, char_switch, restart_button, music_button, settings_button, quit_button, offset_x):
    if pause != True :
        for tile in background:
         window.blit(bg_image, tile)

        for obj in objects:
         obj.draw(window, offset_x)
    
        keyboard.draw(window, offset_x)
        #fire_danger.draw(window, offset_x)
        char_switch.draw(window, offset_x)
        restart_button.draw(window)
        lives.draw(window)
        player.draw(window, offset_x)
    music_button.draw(window)
    settings_button.draw(window)
    quit_button.draw(window)
    pygame.display.update()

def handle_vertical_collision (player, objects, dy):
    collided_objects = []
    for obj in objects : 
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0 :
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0 :
                player.rect.top = obj.rect.bottom
                player.hit_head()
        
            collided_objects.append(obj)

    return collided_objects

def collide (player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_objects = None
    for obj in objects : 
        if pygame.sprite.collide_mask(player, obj):
            collided_objects = obj
            break
    player.move(-dx,0)
    player.update()
    return collided_objects
            
def handle_move (player, objects , pause):
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collide_left = collide (player, objects, -PLAYER_VEL * 2)
    collide_right = collide (player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left and not pause:
        player.move_left(PLAYER_VEL) 
    if keys[pygame.K_RIGHT] and not collide_right and not pause:
        player.move_right(PLAYER_VEL)
    
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check : 
        if obj and obj.name == "fire" :
            player.make_hit(True)

def draw_menu_fade_in(window, opened, music_button, settings_button, quit_button, menu_board, duration):
    if opened == 0 : 
        alpha = 0
        start_time = time.time()
        while alpha < 255:
            elapsed = (time.time() - start_time) / duration
            alpha = min(int(elapsed * 255), 255)
            menu_board.image.set_alpha(alpha)
            music_button.draw(window)
            settings_button.draw(window)
            quit_button.draw(window)
            window.blit(menu_board.image, (menu_board.rect.x, menu_board.rect.y))
            pygame.display.update()

def main (window):
    clock = pygame.time.Clock()
    mute = False
    pause = False
    block_size = 96
    background, bg_image = get_background("Pink.png")               

    #Buttons
    quit_button = Button (WIDTH-70,20,64,64,join("assets", "Menu", "Buttons", "Close.png"),join("assets", "Menu", "Buttons", "Close_clicked.png"))
    settings_button = Button (WIDTH-130, 20,64,64,join("assets", "Menu", "Buttons", "Settings.png"),join("assets", "Menu", "Buttons", "Settings_clicked.png"))
    restart_button = Button(WIDTH-190, 20,64,64, join("assets", "Menu", "Buttons", "Restart.png"),join("assets", "Menu", "Buttons", "Restart_clicked.png"))
    music_button = Button (WIDTH-250,20,64,64,join("assets", "Menu", "Buttons", "Volume.png"),join("assets", "Menu", "Buttons", "Volume_clicked.png"))
    
    #Elements
    player = Player(100,300,50,50)
    lives = Lives (WIDTH // 2 -135, 21, 270,60,join("assets", "Lives", "Lives_4.png") )
    keyboard = Info(200, 10, 250,250, join("assets", "Infos", "keyboard.png"))
    char_switch=Info(600, 100, 300,300, join("assets", "Infos", "char_switch.png"))

    #Menu Elements
    menu_switch = False
    opened = 0
    menu_w = (480 + 480 * 0.2)
    menu_h = (650 + 650 * 0.2)
    menu_board = Menu((WIDTH / 2 - menu_w / 2) , (HEIGHT / 2 - menu_h / 2), menu_w, menu_h, join("assets", "Menu", "Menu.png"))

    #Fires
    fire_danger = Info (5*block_size + 32+30, HEIGHT - block_size * 3 - 100, 216, 100, join("assets", "Infos", "fire_danger.png") )
    fire_1 = Fire(5*block_size + 32, HEIGHT - block_size * 3 - 64, 16, 64)
    fire_2 = Fire(10*block_size + 32, HEIGHT - block_size - 64, 16, 64)
    fire_1.on()
    fire_2.on()


    #The Map
    floor_complete = [Block (i * block_size, HEIGHT - block_size, block_size) for i in range (-(WIDTH*10) // block_size, (WIDTH * 10) // block_size) ]
    test_block = Yajour(block_size * 3, HEIGHT - block_size * 2, block_size)
    #Walls
    wall_left = [Yajour (0, HEIGHT - block_size * (i+2), block_size) for i in range (9)]
    wall_right = [Yajour (21 * block_size, HEIGHT - block_size * (i+2), block_size) for i in range (9)]
    #Floors 
    floor_1 = [Block (i * block_size, HEIGHT - block_size, block_size ) for i in range(4) ]
    floor_2 = [Yajour( (4 + i) * block_size, HEIGHT - block_size * 3, block_size) for i in range(3)]
    floor_3 = [Block ( (7+ i) * block_size, HEIGHT - block_size, block_size) for i in range(6)]
    floor_4 = [Yajour( (13 + i)* block_size, HEIGHT - block_size * 3, block_size) for i in range(1)]
    floor_5 = [Block ( (14+ i) * block_size, HEIGHT - block_size, block_size) for i in range(8)]
    #All Objects
    objects = [fire_1,fire_2,*floor_1,*wall_left, *wall_right, *floor_2, *floor_3,*floor_4,*floor_5 ]

    offset_x = 0
    scroll_area_width = 200
    char_change = 0
    
    run = True
    while run :
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.is_clicked(event.pos) and not pause:
                    player = Player(100, 300, 50, 50)
                    offset_x = 0
                if music_button.is_clicked(event.pos) :
                    if mute == False :
                        mute = True
                        music_button =Button (WIDTH-250,20,64,64,join("assets", "Menu", "Buttons", "Mute.png"),join("assets", "Menu", "Buttons", "Mute_clicked.png"))
                        pygame.mixer.music.pause()
                    elif mute == True :
                        mute = False
                        music_button = Button (WIDTH-250,20,64,64,join("assets", "Menu", "Buttons", "Volume.png"),join("assets", "Menu", "Buttons", "Volume_clicked.png"))
                        pygame.mixer.music.unpause()
                if quit_button.is_clicked (event.pos):
                    print("are you sure you want to quit ?")
                if settings_button.is_clicked (event.pos):
                    menu_switch = not menu_switch
                    pause = not pause

            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_e :
                    run = False 
                    break

                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and player.jump_count <2 and pause != True :
                    player.jump()

                if event.key == pygame.K_c and pause != True :
                     char_change += 1 
                     if char_change > 3 :
                         char_change = 0
                     Player.SPRITES = load_sprite_sheets("MainCharacters", Player.char_list[char_change],32,32,True)

                if event.key == pygame.K_r and pause != True :
                    player = Player(100,300,50,50)
                    offset_x = 0
                    draw_text(window, WIDTH-165 , 80, "Reset !", "Comic Sans MS","White",18, 0.2)
                
    
        lives = Lives (WIDTH // 2 -135, 21, 270,60,join("assets", "Lives", f"Lives_{player.lives_count}.png") )
        if player.lives_count == 0 :
                    lives = Lives (WIDTH // 2 -135, 21, 270,60,join("assets", "Lives", "Lives_0.png") )
                    draw(window, pause, background, bg_image, player, objects, lives, keyboard, fire_danger, char_switch, restart_button, music_button, settings_button, quit_button, offset_x)
                    draw_text(window, WIDTH // 2 - 80, 30, "Game Over !","Comic Sans MS","White",30, 2)
                    player = Player(100,300,50,50)
                    offset_x = 0
                    lives = Lives (WIDTH // 2 -135, 21, 270,60,join("assets", "Lives", "Lives_4.png") )


        # Player falls out of the screen (in construction)
        if player.rect.y > HEIGHT:
            #offset_x = 0
            #pygame.time.delay(500)
            player.rect = pygame.Rect(player.rect.x, 100, 50, 50)
            #player = Player(100, 100, 50, 50)  # Reset player
            player.update_sprite() # Update the sprite immediately after reset
            pygame.time.delay(1000)
            

        #Loops            
        player.loop(FPS)
        fire_1.loop()
        fire_2.loop()

        handle_move (player, objects, pause)
        draw (window, pause, background, bg_image, player, objects, lives, keyboard, fire_danger, char_switch,
        restart_button,settings_button, music_button, quit_button, offset_x)

        #Menu 
        if menu_switch == True :
            #draw_menu_fade_in(window, menu_board, offset_x, duration=1.0)
            draw_menu_fade_in(window, opened, music_button, settings_button, quit_button, menu_board, 3)
            opened = 1
        else :
            opened = 0

        #Background Scrolling
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width * 2) and player.x_vel > 0):
            offset_x += player.x_vel
        elif ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
            
    pygame.quit()
    quit()
 
if __name__  == "__main__":
    main(window)