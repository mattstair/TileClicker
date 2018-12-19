import pygame

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GREY = pygame.Color('grey')


class ScrollWindow():
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
        self.full_surf = pygame.Surface(full_size)
        self.window_surf = pygame.Surface(window_size)
        self.view_surf = self.window_surf.subsurface((0, 0, self.view_size[0], self.view_size[1]))
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

    def do_window(self, surface, pos):
        while True:
            mouse = pygame.mouse.get_pos()
            rel_mouse = (mouse[0]-pos[0], mouse[1]-pos[1])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
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


def main():
    pygame.init()

    offset1 = (50, 50)
    offset2 = (25, 25)

    window1 = ScrollWindow((400, 350), (300, 300), WHITE)
    window1.full_surf.fill(WHITE)
    window2 = ScrollWindow((400, 150), (200, 200), WHITE)
    window2.full_surf.fill(WHITE)
    pygame.draw.rect(window2.full_surf, BLACK, (50, 50, 348, 98), 1)

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
        window2.draw(window1.full_surf, (offset2[0], offset2[1]))
        window1.draw(gameDisplay, (offset1[0], offset1[1]))

        pygame.display.flip()
        clock.tick()

    while True:
        gameDisplay.fill(WHITE)
        mouse = pygame.mouse.get_pos()
        rel_mouse = (mouse[0]-offset1[0], mouse[1]-offset1[1])
        rel_rel_mouse = (rel_mouse[0]-offset2[0]+window1.xpos, rel_mouse[1]-offset2[1]+window1.ypos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if window1.has_h_sb:
                    if window1.h_sb.collidepoint(rel_mouse):
                        window1.moving_h = True
                        window1.start_mouse = rel_mouse
                        window1.start_x = window1.h_sb.left
                if window1.has_v_sb:
                    if window1.v_sb.collidepoint(rel_mouse):
                        window1.moving_v = True
                        window1.start_mouse = rel_mouse
                        window1.start_y = window1.v_sb.top
                if window2.has_h_sb:
                    if window2.h_sb.collidepoint(rel_rel_mouse):
                        window2.moving_h = True
                        window2.start_mouse = rel_rel_mouse
                        window2.start_x = window2.h_sb.left
                if window2.has_v_sb:
                    if window2.v_sb.collidepoint(rel_rel_mouse):
                        window2.moving_v = True
                        window2.start_mouse = rel_rel_mouse
                        window2.start_y = window2.v_sb.top

            if event.type == pygame.MOUSEBUTTONUP:
                window1.moving_h = False
                window1.moving_v = False
                window2.moving_h = False
                window2.moving_v = False

        scroll_window(window1, rel_mouse)
        scroll_window(window2, rel_rel_mouse)
        draw()


if __name__ == '__main__':
    main()
