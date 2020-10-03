import pygame as pg
from pygame.constants import *

url='https://www.google.com/search?q='

player_name = 'Qiaoster'

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 120
bg = pg.image.load('data/images/bg.png')
char = pg.image.load('data/images/idle.png')

all_fonts = pg.font.get_fonts()
#font_name = all_fonts[0]
font_name = 'data/fonts/Georgia.ttf'

PLATFORM_LAYER = 0
PLAYER_LAYER = 1
BOT_LAYER = 1

NUM_BOTS = 4
JACKSTER_CHANCE = 90

winning_score = 40

player_acc = 2 #d wpm/dt
player_friction = -0.8
player_grav = 1.0
player_jump = -27

wpm_factor = 50
avg_wpm = 80
passage_char_limit = 250

PLATFORM_LIST = [(SCREEN_WIDTH // 3, SCREEN_HEIGHT - 220, SCREEN_WIDTH // 3, 40),
                 (SCREEN_WIDTH // 4, SCREEN_HEIGHT - 220 * 2, SCREEN_WIDTH // 3, 30)]

PLATFORM_THICKNESS = 35
plat_limit = 14
plat_y_list = [SCREEN_HEIGHT - 40, SCREEN_HEIGHT * 3 // 5 - 40, SCREEN_HEIGHT // 4 + 10, SCREEN_HEIGHT * 3 // 4]

COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
input_font_size = 20

GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (131,152,171)
RED = (255,69,69)
GHOSTED_TEXT = (149,149,149)
paddingx = 50
paddingy = 50

text_rect = (paddingx,SCREEN_HEIGHT*2//3,SCREEN_WIDTH-2*paddingx,SCREEN_HEIGHT//3-paddingy) #x,y,width,height
calibration_text = 'This text is to calibrate your typing speed. It took the brand two years to develop the perfect $4 Popeyes sandwich.'
calibration_text = 'Meesi.'

typing_dict={
    K_q:'q',K_w:'w',K_e:'e',K_r:'r',K_t:'t',K_y:'y',K_u:'u',K_i:'i',K_o:'o',K_p:'p',
    K_a:'a',K_s:'s',K_d:'d',K_f:'f',K_g:'g',K_h:'h',K_j:'j',K_k:'k',K_l:'l',K_z:'z',K_x:'x',K_c:'c',K_v:'v',K_b:'b',
    K_n:'n',K_m:'m',K_PERIOD:'.',K_LEFTPAREN:'(',K_RIGHTPAREN:')',K_SPACE:' ',K_RSHIFT:'',K_LSHIFT:'', K_COMMA:',', K_SEMICOLON:';',
    K_1:'1',K_2:'2',K_3:'3',K_4:'4',K_5:'5',K_6:'6',K_7:'7',K_8:'8',K_9:'9',K_0:'0', K_MINUS:'-', K_QUOTE: "'"
}

############# FUNCTIONS ###############

#doesn't wrap text
def draw_text(surf, text, size, x, y, color,pos='left'):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if pos == 'left':
        text_rect.topleft = (x, y)
    elif pos == 'mid':
        text_rect.midtop = (x,y)
    surf.blit(text_surface, text_rect)

#wraps text
def drawText(surface, text, color, rect, font_name, aa=False, bkg=None, size=30):
    rect = pg.Rect(rect)
    y = rect.top
    lineSpacing = 2

    font = pg.font.Font(font_name, size)
    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]
    return text #what's chopped off

def get_image(img, width, height):
    # grab an image out of a larger spritesheet
    image = pg.Surface((width, height))
    image.blit(img, (0, 0), (0, 0, width, height))
    # image = pg.transform.scale(image, (width // 2, height // 2))
    return image

#webscraping modifications

def space_caps(s):
    """
    :param s: string
    :return: string with all cap letters with lowercase behind spaced away
    process: identify l,U cases then (strings are immutable) split string s at those l,U places and concatonate them all together in the end
    """
    split_list = []
    insert_list = []
    def isRemoved(letter):
        if ord(letter)>65 and ord(letter)<91: #or (ord(letter)<58 and ord(letter)>47):
            return True
        return False
    def findem(): #find l,U places
        for i in range(len(s)-1):
            if not isRemoved(s[i]) and isRemoved(s[i+1]):
                split_list.append(s[i]+s[i+1])

    findem()
    l = [s]
    for i in split_list: # gives l with all u,l cases split
        l = l[:-1] + l[-1].split(i,1)

    #adds space
    for item in split_list: #'uL'
        insert_list.append(item[0] + ' ' + item[1])


    final_s=''
    for i in range(len(l)-1):
        final_s += l[i] + insert_list[i]
    final_s += l[-1]

    return final_s


