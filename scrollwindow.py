import pygame

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GREY = pygame.Color('grey')


class ScrollWindow(object):
    def __init__(self, full_size, window_size, bg_color):
        self.full_size: tuple = full_size
        self.window_size: tuple = window_size
        self.bg_color = bg_color
        self.sb_thickness = 10
        self.has_h_sb = True
        self.has_v_sb = True
        if full_size[0]-window_size[0]-self.sb_thickness <= 0:
            self.has_h_sb = False
        if full_size[1]-window_size[1]-self.sb_thickness <= 0:
            self.has_v_sb = False
        self.view_size = (window_size[0]-(self.sb_thickness-1)*self.has_v_sb,
                          window_size[1]-(self.sb_thickness-1)*self.has_h_sb)
        self.__full_surf = pygame.Surface(full_size)
        self.__window_surf = pygame.Surface(window_size)
        self.__view_surf = self.window_surf.subsurface((0, 0, self.view_size[0], self.view_size[1]))
        if self.has_h_sb:
            self.h_sb_size = self.view_size[0]/full_size[0]*self.window_size[0]-(self.sb_thickness*self.has_v_sb)
        if self.has_v_sb:
            self.v_sb_size = self.view_size[1]/full_size[1]*self.window_size[1]-(self.sb_thickness*self.has_h_sb)
        self.xpos = 0
        self.ypos = 0
        if self.has_h_sb:
            self.h_sb = pygame.Rect(0, self.window_size[1]-self.sb_thickness, self.h_sb_size, self.sb_thickness)
        if self.has_v_sb:
            self.v_sb = pygame.Rect(self.window_size[0]-self.sb_thickness, 0, self.sb_thickness, self.v_sb_size)
        self.bottom_sq_rect = (self.window_size[0]-self.sb_thickness, self.window_size[1]-self.sb_thickness,
                               self.sb_thickness, self.sb_thickness)
        self.moving_h = False
        self.moving_v = False

    @property
    def full_surf(self):
        if self.__full_surf is None:
            self.__full_surf = pygame.Surface(self.full_size)
        return self.__full_surf

    @property
    def window_surf(self):
        if self.__window_surf is None:
            self.__window_surf = pygame.Surface(self.window_size)
        return self.__window_surf

    @property
    def view_surf(self):
        if self.__view_surf is None:
            self.__view_surf = self.window_surf.subsurface((0, 0, self.view_size[0], self.view_size[1]))
        return self.__view_surf

    def draw(self, surface, pos):
        self.window_surf.fill(self.bg_color)
        self.view_surf.blit(self.full_surf, (-self.xpos, -self.ypos))

        if self.has_h_sb and self.has_v_sb:
            pygame.draw.rect(self.window_surf, BLACK, self.bottom_sq_rect, 1)
        if self.has_h_sb:
            pygame.draw.rect(self.window_surf, GREY, self.h_sb)
            pygame.draw.rect(self.window_surf, BLACK, self.h_sb, 1)
        if self.has_v_sb:
            pygame.draw.rect(self.window_surf, GREY, self.v_sb)
            pygame.draw.rect(self.window_surf, BLACK, self.v_sb, 1)
        pygame.draw.rect(self.view_surf, BLACK, self.view_surf.get_rect(), 1)
        pygame.draw.rect(self.window_surf, BLACK, self.window_surf.get_rect(), 1)
        surface.blit(self.window_surf, pos)

    def scroll(self, pixel_count, vertical=True):
        if vertical and self.has_v_sb:
            if self.full_size[1] < pixel_count - self.view_size[1] + self.ypos < 0:
                return False
            else:
                self.v_sb.top = min(self.view_size[1] - self.v_sb.h,
                                    max(0, self.v_sb.top + pixel_count))
                self.ypos = self.v_sb.top / (self.view_size[1] - self.v_sb_size) * (
                            self.full_size[1] - self.view_size[1])
                return True
        elif not vertical and self.has_h_sb:
            if self.full_size[0] < pixel_count - self.view_size[0] + self.xpos < 0:
                return False
            else:
                self.h_sb.left = min(self.view_size[0]-self.h_sb.w,
                                     max(0, self.h_sb.left+pixel_count))
                self.xpos = self.h_sb.left/(self.view_size[0]-self.h_sb_size)*(self.full_size[0]-self.view_size[0])
                return True
        else:
            return False

    def do_window(self, surface, pos):
        while True:
            mouse = pygame.mouse.get_pos()
            rel_mouse = (mouse[0]-pos[0], mouse[1]-pos[1])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.has_h_sb:
                            if self.h_sb.collidepoint(rel_mouse):
                                self.moving_h = True
                                self.start_mouse = rel_mouse
                                self.start_x = self.h_sb.left
                        if self.has_v_sb:
                            if self.v_sb.collidepoint(rel_mouse):
                                self.moving_v = True
                                self.start_mouse = rel_mouse
                                self.start_y = self.v_sb.top
                    elif event.button == 4:
                        self.scroll(-10)
                    elif event.button == 5:
                        self.scroll(10)
                if event.type == pygame.MOUSEBUTTONUP:
                    self.moving_h = False
                    self.moving_v = False
            if self.moving_h:
                self.h_sb.left = min(self.view_size[0]-self.h_sb.w,
                                     max(0, self.start_x-(self.start_mouse[0]-rel_mouse[0])))
                self.xpos = self.h_sb.left/(self.view_size[0]-self.h_sb_size)*(self.full_size[0]-self.view_size[0])
            if self.moving_v:
                self.v_sb.top = min(self.view_size[1]-self.v_sb.h,
                                    max(0, self.start_y-(self.start_mouse[1]-rel_mouse[1])))
                self.ypos = self.v_sb.top/(self.view_size[1]-self.v_sb_size)*(self.full_size[1]-self.view_size[1])
            self.draw(surface, pos)
            pygame.display.flip()

    def clean(self):
        self.__full_surf = None
        self.__window_surf = None
        self.__view_surf = None


def main():
    pygame.init()

    offset1 = (50, 50)
    offset2 = (25, 25)

    window = ScrollWindow((400, 350), (300, 300), WHITE)
    window.full_surf.fill(WHITE)
    pygame.draw.rect(window.full_surf, BLACK, (50, 50, 348, 98), 1)

    gameDisplay = pygame.display.set_mode((500, 500))
    gameDisplay.fill(WHITE)
    clock = pygame.time.Clock()

    def scroll_window(win, rel_mouse):
        if win.moving_h:
            win.h_sb.left = min(win.view_size[0]-win.h_sb.w,
                                max(0, win.start_x-(win.start_mouse[0]-rel_mouse[0])))
            win.xpos = win.h_sb.left/(win.view_size[0]-win.h_sb_size)*(win.full_size[0]-win.view_size[0])
        if win.moving_v:
            win.v_sb.top = min(win.view_size[1]-win.v_sb.h,
                               max(0, win.start_y-(win.start_mouse[1]-rel_mouse[1])))
            win.ypos = win.v_sb.top/(win.view_size[1]-win.v_sb_size)*(win.full_size[1]-win.view_size[1])

    def draw():
        window.draw(gameDisplay, (offset1[0], offset1[1]))

        pygame.display.flip()
        clock.tick()

    while True:
        gameDisplay.fill(WHITE)
        mouse = pygame.mouse.get_pos()
        rel_mouse = (mouse[0]-offset1[0], mouse[1]-offset1[1])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if window.has_h_sb:
                        if window.h_sb.collidepoint(rel_mouse):
                            window.moving_h = True
                            window.start_mouse = rel_mouse
                            window.start_x = window.h_sb.left
                    if window.has_v_sb:
                        if window.v_sb.collidepoint(rel_mouse):
                            window.moving_v = True
                            window.start_mouse = rel_mouse
                            window.start_y = window.v_sb.top
                elif event.button == 4:
                    if window.window_surf.get_rect().collidepoint(mouse):
                        window.scroll(-10)
                elif event.button == 5:
                    if window.window_surf.get_rect().collidepoint(mouse):
                        window.scroll(10)

            if event.type == pygame.MOUSEBUTTONUP:
                window.moving_h = False
                window.moving_v = False

        scroll_window(window, rel_mouse)
        draw()


if __name__ == '__main__':
    main()
