import pygame as pg
from settings import *
from classes import *
import time

class Game(object):
    def __init__(self):
        pg.init()
        pg.display.set_caption('Not a Typing Test')
        self.clock = pg.time.Clock()
        self.score = 0
        self.screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        #self.screen = pg.display.set_mode([SCREEN_WIDTH,SCREEN_HEIGHT], pg.FULLSCREEN)

        #webscraping
        self.online = False
        self.webscraper = Query(self)
        self.query = ''

        #wpm
        self.wpm = 0
        self.char_typed=0 #correct characters typed
        self.calibrated_wpm = 0

        #accuracy
        self.accuracy = 0
        self.total_char_typed = 0

        #timer
        self.timer = 0
        self.base_time= 0

        #misc
        self.calibrated = False
        self.new_round = True


        self.running = True

    def new(self):
        #input box
        self.input_box=InputBox(SCREEN_WIDTH-300,100,100,30,self,'')


        #sprite groups

        # self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.bots = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

        self.player = Player(text_rect[0]+32,text_rect[1],64,100,self)



        #for debugging
        # self.bot1 = Bot(300,400,64,100,self,color=GRAY)
        # self.bot2 = Bot(300,300,64,100,self)

        #initialize typing text
        self.typing_text=TypingText(SCREEN_WIDTH//2,SCREEN_HEIGHT//4*3,BLACK,font_name,20,self)



        self.run()

    def run(self):
        self.playing=True
        #Main game loop
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        self.typing_text.update()
        self.input_box.update()



        #timer

        # if self.typing_text.start:
        #     self.base_time = time.time()
        if self.typing_text.start:
            self.timer = time.time() - self.base_time

        ####### calculating wpm (words/ms * 1000/60)

        # noninstantaneous implementation
        """
        char_count = (len(passage) + 1)/5 
        if self.timer > 0: self.wpm = int(char_count/(self.timer/60))
        else: self.wpm =0
        """

        #instantaneous wpm calculator
        if self.timer > 0.09: self.wpm = (self.char_typed/5)/(self.timer/60)
        else: self.wpm = 0

        #instantaneous accuracy calculator
        if self.total_char_typed>0 and self.typing_text.start: self.accuracy = self.char_typed/self.total_char_typed * 100
        elif self.total_char_typed == 0: self.accuracy =0

        #moving screen to the right
        if self.player.rect.right > SCREEN_WIDTH *5// 7:

            self.player.pos.x -= abs(self.player.vel.x)
            for bot in self.bots:
                bot.pos.x -= abs(int(self.player.vel.x))

            for plat in self.platforms:
                if plat.type == 'platform':
                    plat.rect.x -= abs(int(self.player.vel.x))
                    if plat.rect.right < 0:
                        plat.kill()


        #spawning in bots and new round
        if self.calibrated and self.new_round:
            for bot in self.bots:
                bot.kill()

            y_datum = self.player.y - self.player.height

            for i in range(6):
                Bot(self.player.x, y_datum-i*45, 64, 40, self, color = GRAY)

            # self.bot1 = Bot(self.player.x, y_datum, 64, 40, self, color=GRAY)
            # self.bot2 = Bot(self.player.x, y_datum-40, 64, 40, self)
            # self.bot3 = Bot(self.player.x, )
            self.typing_text.reset_game()

            for platform in self.platforms:
                platform.kill()


            self.new_round = False

        #generating new platforms
        while len(self.platforms) < plat_limit:
            width = 100
            maxdiff = 700

            l= [(SCREEN_WIDTH + i) for i in range(300,1000,width)]
            self.tempx = random.choice(l)


            self.tempy = 500
            Platform(self.tempx, self.tempy, width, PLATFORM_THICKNESS, 'platform', self)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            #input box event
            if self.online:
                self.input_box.handle_event(event)

            if event.type == pg.KEYDOWN:
                self.typing_text.wrong_letter_flag = False  # to penalize for multiple wrong keys even if stuck
                self.typing_text.end_of_passage=False #if after calibration starts typing
                self.typing_text.feed_in = event.unicode
                if event.key not in [K_RSHIFT, K_LSHIFT]: self.total_char_typed += 1
                print(self.typing_text.feed_in)

                #before i found out about event.unicode
                # if event.key in typing_dict.keys() and event.mod and KMOD_SHIFT: #capitalization
                #     self.typing_text.wrong_letter_flag = False #to penalize for multiple wrong keys even if stuck
                #     self.typing_text.end_of_passage=False #if after calibration starts typing
                #     self.typing_text.feed_in = typing_dict[event.key].capitalize()
                #     print(self.typing_text.feed_in)
                #     if event.key not in [K_RSHIFT, K_LSHIFT]: self.total_char_typed += 1
                #
                # elif event.key in typing_dict.keys(): #lowercase and punctuation
                #     self.typing_text.wrong_letter_flag = False
                #     self.typing_text.end_of_passage = False
                #     self.typing_text.feed_in = typing_dict[event.key]
                #     print(self.typing_text.feed_in)
                #     if event.key not in [K_RSHIFT, K_LSHIFT]: self.total_char_typed+=1
                #
                # else:
                #     print('Not a valid key!')


    def draw(self):
        #self.screen.blit(bg,(0,0))
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        pg.draw.rect(self.screen, WHITE, (paddingx-2,SCREEN_HEIGHT*2//3,SCREEN_WIDTH-2*paddingx + 10,SCREEN_HEIGHT//3-paddingy))
        self.typing_text.draw()

        draw_text(self.screen,'WPM: ' + str(round(self.wpm)),30, 100,100, WHITE)
        draw_text(self.screen, 'Timer: ' + str(round(self.timer,1)) + ' seconds', 30 , 100, 70, WHITE)
        draw_text(self.screen, f'Calibrated WPM: {round(self.calibrated_wpm)}' , 30, 100, 130, WHITE)
        draw_text(self.screen, f'Accuracy: {round(self.accuracy, 2)}%', 30, 100, 160, WHITE)
        draw_text(self.screen, "Begin typing to start timer.", 30, SCREEN_WIDTH//2, 30, WHITE, pos = 'mid')

        self.input_box.draw(self.screen)




        pg.display.update()

    def show_start_screen(self):
        pass #show online status

    def show_go_screen(self):
        if not self.running:
            return

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()