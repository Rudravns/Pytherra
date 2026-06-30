import pygame as pg
import threading
import time
import utils

class Loading():
    def __init__(self, screen):
        self.screen = screen

        self.active_tasks = []

    def run(self):
        self.setup_threads()

        self.first.start()
        self.second.start()
        self.third.start()

        while len(self.active_tasks) > 0:
            self.events()
            self.display()
    
    def setup_threads(self):
        self.first = threading.Thread(target=self.thread1)
        self.second = threading.Thread(target=self.thread2)
        self.third = threading.Thread(target=self.thread3)

        self.active_tasks.append("1")
        self.active_tasks.append("2")
        self.active_tasks.append("3")
    
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.screen.quit()

    def display(self):
        self.screen.fill((0, 0, 0))
        utils.draw_text(self.screen, "Loading Game...", int(40 * utils.SCALE["overall"]), (255, 255, 255), (400 * utils.SCALE["width"], 400 * utils.SCALE["height"]))
        utils.draw_text(self.screen, f"{self.active_tasks}", int(40 * utils.SCALE["overall"]), (255, 255, 255), (400 * utils.SCALE["width"], 440 * utils.SCALE["height"]))

        pg.display.flip()
    
    def thread1(self):
        time.sleep(8)
        self.active_tasks.remove("1")
    
    def thread2(self):
        time.sleep(2)
        self.active_tasks.remove("2")
    
    def thread3(self):
        time.sleep(4)
        self.active_tasks.remove("3")