import pygame

white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 100, 0)


class StatusSquare():
    def __init__(self, w, h, color, perc=0.0, alpha=150):
        self.w = w
        self.h = h
        self.rect = pygame.Rect(0, 0, w, h)
        self.color = color
        self.value = perc
        self.surf = pygame.Surface((w, h))
        self.surf.set_colorkey(black)
        self.surf.set_alpha(alpha)

    def increment(self, inc):
        amt = min(100, max(0, self.value + inc))
        self.value = amt
        self.draw()

    def set(self, num):
        amt = min(100, max(0, num))
        self.value = amt
        self.draw()

    def draw(self):
        pointlist = []
        pointlist.append(self.rect.midtop)
        pointlist.append(self.rect.center)
        if self.value < 12.5:
            xval = self.value/12.5*(self.w/2)+self.w/2
            pointlist.append((xval, 0))
        elif self.value < 37.5:
            yval = (self.value - 12.5)/25*self.h
            pointlist.append((self.w, yval))
            pointlist.append(self.rect.topright)
        elif self.value < 62.5:
            xval = self.w - (self.value - 37.5)/25*self.w
            pointlist.append((xval, self.h))
            pointlist.append(self.rect.bottomright)
            pointlist.append(self.rect.topright)
        elif self.value < 87.5:
            yval = self.h - (self.value - 62.5)/25*self.h
            pointlist.append((0, yval))
            pointlist.append(self.rect.bottomleft)
            pointlist.append(self.rect.bottomright)
            pointlist.append(self.rect.topright)
        elif self.value < 100:
            xval = (self.value - 87.5)/12.5*(self.w/2)
            pointlist.append((xval, 0))
            pointlist.append(self.rect.topleft)
            pointlist.append(self.rect.bottomleft)
            pointlist.append(self.rect.bottomright)
            pointlist.append(self.rect.topright)
        else:
            pointlist = [(0, 0), (self.w, 0), (self.w, self.h), (0, self.h)]
        self.surf.fill(black)
        pygame.draw.polygon(self.surf, self.color, pointlist)


def main():
    pygame.init()

    tile = StatusSquare(50, 50, green)

    gameDisplay = pygame.display.set_mode((500, 500))
    gameDisplay.fill(white)
    clock = pygame.time.Clock()

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        tile.set(mouse[0]/500*100)
        tile.draw()
        gameDisplay.fill(white)
        pygame.draw.rect(gameDisplay, black, (100, 100, 50, 50), 1)
        pygame.draw.rect(gameDisplay, black, (112, 112, 25, 25))
        gameDisplay.blit(tile.surf, (100, 100))
        pygame.display.flip()
        clock.tick(10)


if __name__ == '__main__':
    main()
