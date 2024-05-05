import pygame

class Button:
    def __init__(self, x_coord, y_coord, image, sound, scale=1, hover_scale=1.1):
        width = image.get_width()
        height = image.get_height()
        self.modified_width = int(width * scale)
        self.modified_height = int(height * scale)
        self.modified_hover_width = int(width * hover_scale)
        self.modified_hover_height = int(height * hover_scale)
        
        self.sound = sound
        self.image = pygame.transform.scale(image, (self.modified_width, self.modified_height))
        self.hover_image = pygame.transform.scale(image, (self.modified_hover_width, self.modified_hover_height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x_coord, y_coord)
        self.clicked = False
        self.mouse_down = False
        self.mouse_click = False
                
    def draw(self, surface):
        action = False
        # get mouse postition
        pos = pygame.mouse.get_pos()
        
        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            hover_width = self.hover_image.get_width()
            hover_x_coord = int(self.rect.x - (hover_width - self.modified_width) / 2)
            # draw button on screen
            surface.blit(self.hover_image, (hover_x_coord, self.rect.y))
            if pygame.mouse.get_pressed()[0] == 1:
                self.mouse_down = True
            if pygame.mouse.get_pressed()[0] == 0 and self.mouse_down == True:
                self.mouse_click = True
        else:
            # draw button on screen
            surface.blit(self.image, (self.rect.x, self.rect.y))
            if pygame.mouse.get_pressed()[0] == 0:
                self.mouse_down = False
            
        if self.mouse_click == True:
            pygame.mixer.Sound.play(self.sound)
            action = True
            self.mouse_down = False
            self.mouse_click = False
        
        return action