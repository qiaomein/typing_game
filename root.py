import pygame as pg
from settings import *
from classes import *
import time

class Game(object):
    def __init__(self):
        pg.init()
        pg.display.set_caption('Not a Typing Test')

        pg.display.set_icon(programIcon)
        self.clock = pg.time.Clock()
        self.score = 0
        self.screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        #self.screen = pg.display.set_mode([SCREEN_WIDTH,SCREEN_HEIGHT], pg.FULLSCREEN)

        self.player_name = ''

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
        self.jackster_round = False
        self.running = True

    def new(self):
        #input box
        self.input_box=InputBox(SCREEN_WIDTH//2,120,200,30,self,'',position = 'mid')

        #buttons
        self.reset_game_button = GameButton(100,50,150,35,'reset_game',self,position = 'mid')
        self.random_fact_button = GameButton(SCREEN_WIDTH*3//4, 120, 150, 30, 'random_fact',self, text = 'Random Fact',position = 'mid')

        #scoreboard
        self.scoreboard = Scoreboard(SCREEN_WIDTH//2,SCREEN_HEIGHT//4,SCREEN_WIDTH//2,50,self)

        #sprite groups

        # self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.bots = pg.sprite.Group()
        self.jacksters = pg.sprite.Group()
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

        #bugfix on calibrated wpm
        if self.typing_text.end_of_passage:
            self.reset_game_button.resetted = False


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
        if self.timer > 0.1: self.wpm = (self.char_typed/5)/(self.timer/60)
        else: self.wpm = 0

        #instantaneous accuracy calculator
        if self.total_char_typed>0 and self.typing_text.start: self.accuracy = self.char_typed/self.total_char_typed * 100
        elif self.total_char_typed == 0: self.accuracy =0

        #moving screen to the right
        if self.player.rect.right > SCREEN_WIDTH *5// 7:

            self.player.pos.x -= abs(self.player.vel.x)
            for bot in self.bots:
                bot.pos.x -= abs(int(self.player.vel.x))

            for jackster in self.jacksters:
                jackster.pos.x -= abs(int(self.player.vel.x))

            for plat in self.platforms:
                if plat.type == 'platform':
                    plat.rect.x -= abs(int(self.player.vel.x))
                    if plat.rect.right < 0:
                        plat.kill()


        #spawning in bots and new round
        if self.calibrated and self.new_round:
            for bot in self.bots:
                bot.kill()
            for jackster in self.jacksters:
                jackster.kill()

            y_datum = self.player.y - self.player.height

            for i in range(NUM_BOTS):
                Bot(self.player.x, y_datum-i*90, 64, 90, self, color = GRAY)

            self.player.pos = vec(text_rect[0] + 32, text_rect[1])

            # self.bot1 = Bot(self.player.x, y_datum, 64, 40, self, color=GRAY)
            # self.bot2 = Bot(self.player.x, y_datum-40, 64, 40, self)
            # self.bot3 = Bot(self.player.x, )
            # self.typing_text.reset_game()

            for platform in self.platforms:
                platform.kill()

            jackster_chance = random.randint(1,100)
            if jackster_chance<JACKSTER_CHANCE:
                Jackster(self.player.x, y_datum-(NUM_BOTS+1)*70, 64, 40, self, color = GREEN)
                self.jackster_round = True
            else:
                self.jackster_round = False



            self.new_round = False

        #generating new platforms
        # while len(self.platforms) < plat_limit:
        #     width = 100
        #     maxdiff = 700
        #
        #     l= [(SCREEN_WIDTH + i) for i in range(300,1000,width)]
        #     self.tempx = random.choice(l)
        #
        #     self.tempy = 500
        #     Platform(self.tempx, self.tempy, width, PLATFORM_THICKNESS, 'platform', self)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            #input box event
            if self.online:
                self.input_box.handle_event(event)

            #if reset game button is pressed
            self.reset_game_button.handle_event(event)

            self.random_fact_button.handle_event(event)

            if event.type == pg.KEYDOWN:
                self.typing_text.wrong_letter_flag = False  # to penalize for multiple wrong keys even if stuck
                if not self.typing_text.end_of_passage: self.typing_text.feed_in = event.unicode
                self.typing_text.end_of_passage=False #if after calibration starts typing

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
        self.screen.fill(WHITE)
        self.screen.blit(bg,(0,0))

        self.all_sprites.draw(self.screen)
        # pg.draw.rect(self.screen, WHITE, (paddingx-2,SCREEN_HEIGHT*2//3,SCREEN_WIDTH-2*paddingx + 10,SCREEN_HEIGHT//3-paddingy))
        self.typing_text.draw()
        if self.typing_text.end_of_passage:
            self.scoreboard.draw()

        draw_text(self.screen,'WPM: ' + str(round(self.wpm)),30, 70,750, BLACK)
        draw_text(self.screen, 'Timer: ' + str(round(self.timer,1)) + ' s', 30 , 230, 750, BLACK)
        draw_text(self.screen, f'Calibrated WPM: {round(self.calibrated_wpm)}' , 25, 480, 755, BLACK)
        draw_text(self.screen, f'Accuracy: {round(self.accuracy, 2)}%', 30, 750, 750, BLACK)

        if not self.typing_text.start:
            draw_text(self.screen, f"Begin typing to start timer, {self.player_name}.", 30, SCREEN_WIDTH//2, 30, BLACK, pos = 'mid')


        if not self.typing_text.end_of_passage and self.calibrated and not self.typing_text.start:
            draw_text(self.screen, f'Learn something new:', 20, 150,self.input_box.rect[1],BLACK)
            self.input_box.draw(self.screen)
            self.random_fact_button.draw(self.screen)

        self.reset_game_button.draw(self.screen)


        pg.display.update()

    def show_start_screen(self):
        #show online status
        named = False
        # start screen input name
        self.get_player_name = InputBox(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 200, 30, self,position = 'mid')
        while not named:
            self.clock.tick(FPS)

            self.screen.fill((52,100,235))

            if self.online:
                online_text = 'Online'
                color = GREEN
            else:
                online_text = 'Offline'
                color = (255,0,0)

            draw_text(self.screen, f'Status: {online_text}', 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180, color,
                      pos='mid')


            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    named = True

                # input box event
                self.get_player_name.get_name(event)

            self.get_player_name.draw(self.screen)
            draw_text(self.screen,'Wasgoodies how may I address you?', 50, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100, BLACK, pos = 'mid')

            self.get_player_name.update()
            if self.player_name != '' and len(self.player_name)>1:
                named = True


            pg.display.update()


        # self.wait_for_click()

    def wait_for_click(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN and self.running:
                    waiting = False

    def show_go_screen(self):
        if not self.running:
            return


        self.wait_for_click()





g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()