import pygame


class StatusBar(pygame.Rect):
    def __init__(self, display, x, y, w, h, l_color, r_color, o_color,
                 maximum=100, val=0):
        super().__init__(x, y, w, h)
        self.display = display
        self.l_color = l_color
        self.r_color = r_color
        self.o_color = o_color
        self.maximum = maximum
        self.val = val

    def incr(self, inc):
        if 0 < self.val < self.maximum:
            self.val = max(0, min(self.maximum, self.val + inc))

    def get_rect(self):
        return [self.x, self.y, self.w, self.h]

    def draw(self):
        position = (self.val / self.maximum * self.w)
        if position == 0:
            pygame.draw.rect(self.display, self.r_color, self.get_rect())
            pygame.draw.rect(self.display, self.o_color, self.get_rect(), 1)
        elif position == self.w:
            pygame.draw.rect(self.display, self.l_color, self.get_rect())
            pygame.draw.rect(self.display, self.o_color, self.get_rect(), 1)
        else:
            l_rect = (self.x, self.y, position, self.h)
            r_rect = (self.x + position, self.y, self.w - position, self.h)
            pygame.draw.rect(self.display, self.l_color, l_rect)
            pygame.draw.rect(self.display, self.r_color, r_rect)
            pygame.draw.rect(self.display, self.o_color, self.get_rect(), 1)

    def check_mouseover(self, relmouse):
        if ((self.x + self.w > relmouse > self.x
             and self.y + self.h > relmouse > self.y)):
            return True
