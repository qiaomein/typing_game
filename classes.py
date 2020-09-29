from settings import *
import pygame as pg
import time
import random
from bs4 import BeautifulSoup
import requests

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_SPACE,
    K_c
)

from pygame.constants import *

vec = pg.math.Vector2

# relate gross wpm or net wpm to speed directly?

class Player(pg.sprite.Sprite):
    def __init__(self, x,y,width,height,game):
        self.groups= game.all_sprites
        self._layer = PLAYER_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.last_update = 0
        self.game=game
        self.walking=False
        self.jumping = False


        self.image = get_image(pg.image.load("data/images/idle.png"), self.width, self.height)
        self.image.set_colorkey(BLACK)
        self.current_frame = 0

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.pos = vec(self.x,self.y)
        self.vel = vec(0,0)
        self.acc = vec(0,0)

        # images
        self.walkRight = [pg.image.load('data/images/run1.png'), pg.image.load('data/images/run2.png'),
                          pg.image.load('data/images/run3.png'), pg.image.load('data/images/run4.png'),
                          pg.image.load('data/images/run5.png'), pg.image.load('data/images/run6.png')]
        for i in self.walkRight:
            i.set_colorkey(BLACK)
        self.walkLeft = []
        for frame in self.walkRight:
            frame.set_colorkey(BLACK)
            self.walkLeft.append(pg.transform.flip(frame, True, False))


    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        if self.walking:
            if self.game.wpm != 0: animated_frames = 4000/self.game.wpm
            else: animated_frames = 60
            if now - self.last_update > animated_frames:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walkRight)
                bottom = self.rect.bottom
                self.image = self.walkRight[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        if not self.jumping and not self.walking:
            self.image = pg.image.load("data/images/idle.png")
            self.rect = self.image.get_rect()

        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        self.animate()
        pressed_keys = pg.key.get_pressed()
        #self.acc = vec (0,player_grav)

        #relating wpm to player speed

        self.acc.x = self.game.wpm/wpm_factor
        self.acc.x += self.vel.x * player_friction + self.game.typing_text.streak/100
        self.vel.x += self.acc.x



        self.pos += self.vel + self.acc

        #for border bounded player movement
        if self.pos.x <= 0:
            self.pos.x = 0
        if self.pos.x >= SCREEN_WIDTH - self.width:
            self.pos.x = SCREEN_WIDTH - self.width

        #for player to loop back
        # if self.pos.x >= SCREEN_WIDTH + self.width:
        #     self.pos.x = -self.width // 2

        self.rect.midbottom = self.pos

class Bot(pg.sprite.Sprite):
    def __init__(self,x,y,width,height,game,color=WHITE):
        self.groups = game.all_sprites, game.bots
        self._layer = BOT_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color=color
        self.last_update = 0
        self.current_frame = 0
        self.walking = False
        self.game = game
        self.wpm = random.randint(round(self.game.calibrated_wpm)-30, round(self.game.calibrated_wpm) + 2)

        # self.image = get_image(pg.image.load("data/images/idle.png"), self.width, self.height)
        # self.rect = self.image.get_rect()

        self.image = pg.Surface((self.width, self.height))
        self.image.fill(self.color)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.pos = vec(self.x, self.y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        #graphics
        self.walkLeft = [pg.image.load('data/images/kiwil1.png'), pg.image.load('data/images/kiwil2.png'),
                          pg.image.load('data/images/kiwil3.png'), pg.image.load('data/images/kiwil4.png'),
                          pg.image.load('data/images/kiwil5.png')]
        for i in self.walkLeft:
            i.set_colorkey(BLACK)

        self.walkRight = []
        for frame in self.walkLeft:
            frame.set_colorkey(BLACK)
            self.walkRight.append(pg.transform.flip(frame, True, False))

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        if self.walking:
            if self.game.wpm != 0:
                animated_frames = 4000 / self.wpm
            else:
                animated_frames = 60
            if now - self.last_update > animated_frames:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walkRight)
                bottom = self.rect.bottom
                self.image = self.walkRight[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        else:
            self.image = self.walkRight[0]
            self.rect = self.image.get_rect()

        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        self.animate()
        self.rect.midbottom = self.pos

        #motion to wpm
        if self.game.typing_text.start:
            self.acc.x = self.wpm / wpm_factor
            self.acc.x += self.vel.x * player_friction
            self.vel.x += self.acc.x

        #self.vel.x = self.wpm / 100

        self.pos += self.vel + self.acc

class Jackster(pg.sprite.Sprite):
    def __init__(self,x,y,width,height,game,color=WHITE):
        self.groups = game.all_sprites
        self._layer = BOT_LAYER
        pg.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color=color
        self.last_update = 0
        self.current_frame = 0
        self.walking = False
        self.game = game
        self.wpm = random.randint(round(self.game.calibrated_wpm)-30, round(self.game.calibrated_wpm) + 2)

        # self.image = get_image(pg.image.load("data/images/idle.png"), self.width, self.height)
        # self.rect = self.image.get_rect()

        self.image = pg.Surface((self.width, self.height))
        self.image.fill(self.color)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.pos = vec(self.x, self.y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        #graphics
        self.walkLeft = [pg.image.load('data/images/kiwil1.png'), pg.image.load('data/images/kiwil2.png'),
                          pg.image.load('data/images/kiwil3.png'), pg.image.load('data/images/kiwil4.png'),
                          pg.image.load('data/images/kiwil5.png')]
        for i in self.walkLeft:
            i.set_colorkey(BLACK)

        self.walkRight = []
        for frame in self.walkLeft:
            frame.set_colorkey(BLACK)
            self.walkRight.append(pg.transform.flip(frame, True, False))

    def animate(self):
        # now = pg.time.get_ticks()
        # if self.vel.x != 0:
        #     self.walking = True
        # else:
        #     self.walking = False
        #
        # if self.walking:
        #     if self.game.wpm != 0:
        #         animated_frames = 4000 / self.wpm
        #     else:
        #         animated_frames = 60
        #     if now - self.last_update > animated_frames:
        #         self.last_update = now
        #         self.current_frame = (self.current_frame + 1) % len(self.walkRight)
        #         bottom = self.rect.bottom
        #         self.image = self.walkRight[self.current_frame]
        #         self.rect = self.image.get_rect()
        #         self.rect.bottom = bottom
        #
        # else:
        #     self.image = self.walkRight[0]
        #     self.rect = self.image.get_rect()
        #
        # self.mask = pg.mask.from_surface(self.image)
        pass

    def update(self):
        self.animate()
        self.rect.midbottom = self.pos

        #motion to wpm
        if self.game.typing_text.start:
            self.acc.x = self.wpm / wpm_factor
            self.acc.x += self.vel.x * player_friction
            self.vel.x += self.acc.x

        #self.vel.x = self.wpm / 100

        self.pos += self.vel + self.acc

class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, type, game):
        self.groups = game.all_sprites, game.platforms
        self._layer = PLATFORM_LAYER
        self.game = game
        pg.sprite.Sprite.__init__(self, self.groups)
        self.width = width
        self.height = height
        self.image = get_image(pg.image.load('data/images/platform.png'),self.width,self.height)
        self.image.set_colorkey(BLACK)


        self.type = type
        # if self.type == 'platform':
        #     self.image.fill(GREEN)
        # else:
        #     self.image.fill((0, 0, 128))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class TypingText(object):
    def __init__(self,x,y,color,font,size,game):
        self.x=x
        self.y=y
        self.color=color
        self.size=size
        self.font=font
        self.game=game
        self.start = False
        self.streak = 0
        self.load_passage()

        self.feed_in=''
        self.passage_clone=self.passage[:]

        self.ghost_passage = ''
        self.passage_letter=self.passage[0]
        self.end_of_passage = False
        self.wrong_letter_flag = False

    def load_passage(self): #sets self.passage to passage
        with open('data/preloads.txt', 'r') as f:
            contents = f.read()
        self.passage = random.choice(contents.split('\n\n'))
        #for debugging
        if not self.game.calibrated:
            self.passage = calibration_text

    def draw(self):

        #draw_text(self.game.screen, passage, self.size, self.x, self.y, self.color)
        drawText(self.game.screen,self.passage_clone,BLACK,text_rect,font_name,aa = True,size = 25)
        #drawText(self.game.screen, self.ghost_passage, GHOSTED_TEXT, text_rect, font_name, aa=True, size=25)


    def update(self):
        if not self.end_of_passage and not self.game.input_box.active:
            self.passage_letter = self.passage_clone[0]
            if self.feed_in == self.passage_letter and not self.start: #starting test
                self.start = True
                self.game.base_time = time.time()
                self.next_letter()
            elif self.feed_in == self.passage_letter:
                self.next_letter()
            elif self.feed_in != self.passage_letter and (self.feed_in != '') and not self.wrong_letter_flag and self.start: #user types wrong letter
                self.wrong_letter()

    def next_letter(self): #letter is correct
        self.wrong_letter_flag = False
        self.streak += 1
        print(f'Streak: {self.streak} letters in a row!')
        if len(self.passage_clone) > 1:
            self.game.char_typed += 1
            self.ghost_passage += self.passage_clone[:1]
            if len(self.passage_clone) > 1:
                self.passage_clone = self.passage_clone[1:]
            else:
                self.passage_clone = '' #to correct for wrong_letter spam
            print('next letter')
            print('ghost passage: '+ self.ghost_passage)
            self.feed_in = ''
        else:
            print('end of passage')
            if not self.game.calibrated:
                self.game.calibrated=True
                print(f'{self.game.calibrated_wpm},{self.game.wpm}')
                self.game.calibrated_wpm = self.game.wpm
            self.load_passage()
            self.passage_clone = self.passage
            self.reset_game()


    #count wrong letters to calculate net wpm

    def wrong_letter(self): #penalize for multiple wrong keys even if stuck
        print('Wrong letter')
        if self.streak>0: self.streak /= 2
        else: self.streak = 0
        self.wrong_letter_flag = True

    def reset_game(self):
        self.end_of_passage = True

        if self.game.calibrated and not self.game.new_round and not self.game.input_box.active:
            print(f'{self.game.calibrated_wpm},{self.game.wpm}')
            self.game.calibrated_wpm = (self.game.wpm + self.game.calibrated_wpm) /2


        self.start = False
        self.game.new_round = True
        self.game.char_typed = 0
        self.streak = 0
        self.game.total_char_typed = 0
        self.game.player.vel.x = 0
        self.game.player.pos = vec(text_rect[0]+32,text_rect[1])


class InputBox:
    def __init__(self, x, y, w, h,game, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = pg.font.Font(font_name, input_font_size).render(text, True, self.color)
        self.active = False
        self.game = game

    def handle_event(self, event):
        if self.game.calibrated:
            if event.type == pg.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = not self.active
                else:
                    self.active = False
                # Change the current color of the input box.
                self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            if event.type == pg.KEYDOWN:
                if self.active:
                    if event.key == pg.K_RETURN: #game query set to user input,
                        self.game.query = self.text
                        self.game.webscraper.fetch()
                        self.text = ''
                        self.active = False
                    elif event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.text += event.unicode
                    # Re-render the text.
                    self.txt_surface = pg.font.Font(font_name, input_font_size).render(self.text, True, self.color)
                self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)

class Query(object):
    def __init__(self,game):
        self.game = game
        self.query = ''
        try:
            self.soup = requests.get(f'{url}{self.query}').text
            self.game.online = True
        except:
            self.game.online = False
        self.a = ''

    def fetch(self):
        self.query = self.game.query.replace('','+')
        self.source = requests.get(f'{url}{self.query}').text
        self.soup = BeautifulSoup(self.source, 'lxml')


        for summary in self.soup.find_all('div', id = 'main'):
            try:
                self.a = summary.text
                self.format_a()
                if 'View allView all' not in self.a:
                    print('ran through try1')
                    self.a = self.a.split('View all')[1]
                    self.a = space_caps(self.a).replace('  ', ' ')
                    self.truncate_a()
                    if 'Metacritic' in self.a and 'Rotten Tomatoes' in self.a:
                        self.a = self.a.split('Metacritic ')[1]
                    print(self.a)
                    self.game.typing_text.reset_game()
                    self.game.typing_text.passage = self.a
                    self.game.typing_text.passage_clone = self.game.typing_text.passage

                else:
                    print('ran through try2')
                    self.a = self.a.split('resultsVerbatim')[1].split('View allView all')[0]
                    self.a = space_caps(self.a).replace('  ', ' ')
                    self.truncate_a()
                    if 'Metacritic' in self.a and 'Rotten Tomatoes' in self.a:
                        self.a = self.a.split('Metacritic ')[1]
                    print(self.a)
                    self.game.typing_text.reset_game()
                    self.game.typing_text.passage = self.a
                    self.game.typing_text.passage_clone = self.game.typing_text.passage
            except:
                self.a = summary.text
                self.format_a()
                self.a = self.a.split('resultsVerbatim')[1]
                self.a = space_caps(self.a).replace('  ', ' ')
                print('ran through except')
                self.truncate_a()
                if 'Metacritic' in self.a and 'Rotten Tomatoes' in self.a:
                    self.a = self.a.split('Metacritic ')[1]
                print(self.a)
                self.game.typing_text.reset_game()
                self.game.typing_text.passage = self.a
                self.game.typing_text.passage_clone = self.game.typing_text.passage

    def format_a(self):
        self.a = self.a.replace('·', ' ')
        self.a = self.a.replace('|', '/')
        self.a = self.a.replace('›', '/')
        self.a = self.a.replace('\n', ' ').replace('\t',' ')

    def truncate_a(self):
        """
        :return: truncates self.a at a word
        """
        if self.a[passage_char_limit] == ' ':
            self.a = self.a[:passage_char_limit]
        else:
            for i in range(passage_char_limit,len(self.a)):
                if self.a[i] == ' ':
                    break
            self.a = self.a[:i]