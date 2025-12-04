import pygame

pygame.init()

WHITE, BLACK = (255,255,255), (0,0,0)

screen = pygame.display.set_mode((700, 500))
pygame.display.set_caption("Text Editor")
clock = pygame.time.Clock()

class ScreenController:
    def __init__(self, screen):
        self.scroll_top = 0
        self.padding_x = 20
        self.padding_y = 30

class TypingOptions:
    def __init__(self):
        self.caps = False
        self.ctrl = False
        self.char_map = { pygame.K_SPACE: " ", pygame.K_EXCLAIM: "!", pygame.K_QUOTEDBL: "\"", pygame.K_HASH: "#", pygame.K_DOLLAR: "$", pygame.K_AMPERSAND: "&", pygame.K_QUOTE: "'", pygame.K_LEFTPAREN: "(", pygame.K_RIGHTPAREN: ")", pygame.K_ASTERISK: "*", pygame.K_PLUS: "+", pygame.K_COMMA: ",", pygame.K_MINUS: "-", pygame.K_PERIOD: ".", pygame.K_SLASH: "/", pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3", pygame.K_4: "4", pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8", pygame.K_9: "9", pygame.K_COLON: ":", pygame.K_SEMICOLON: ";", pygame.K_LESS: "<", pygame.K_EQUALS: "=", pygame.K_GREATER: ">", pygame.K_QUESTION: "?", pygame.K_AT: "@", pygame.K_LEFTBRACKET: "[", pygame.K_BACKSLASH: "\\", pygame.K_RIGHTBRACKET: "]", pygame.K_CARET: "^", pygame.K_UNDERSCORE: "_", pygame.K_BACKQUOTE: "`", pygame.K_a: "a", pygame.K_b: "b", pygame.K_c: "c", pygame.K_d: "d", pygame.K_e: "e", pygame.K_f: "f", pygame.K_g: "g", pygame.K_h: "h", pygame.K_i: "i", pygame.K_j: "j", pygame.K_k: "k", pygame.K_l: "l", pygame.K_m: "m", pygame.K_n: "n", pygame.K_o: "o", pygame.K_p: "p", pygame.K_q: "q", pygame.K_r: "r", pygame.K_s: "s", pygame.K_t: "t", pygame.K_u: "u", pygame.K_v: "v", pygame.K_w: "w", pygame.K_x: "x", pygame.K_y: "y", pygame.K_z: "z", pygame.K_KP_DIVIDE: "/", pygame.K_KP_MULTIPLY: "*", pygame.K_KP_MINUS: "-", pygame.K_KP_PLUS: "+", pygame.K_KP_EQUALS: "=", }

    def is_ctrl(self):
        return self.ctrl
    
    def is_character_in_char_set(self, letter):
        return letter in self.char_map

    def get_character(self, keypress):
        return self.char_map[keypress]

    def is_caps(self):
        return self.caps

    def flip_caps(self):
        self.caps = not self.caps

    def set_ctrl(self, boolean):
        self.ctrl = boolean

class Text:
    def __init__(self):
        self.before_cursor = ""
        self.after_cursor = ""

    def add_character(self, letter, caps):
        if caps: self.before_cursor += letter.upper()
        else: self.before_cursor += letter

    def remove_character(self, is_backspace):
        if self.before_cursor != "" and is_backspace: self.before_cursor = self.before_cursor[:-1]
        elif self.after_cursor != "" and not is_backspace: self.after_cursor = self.after_cursor[1:]

running = True
typingOptions = TypingOptions()
text = Text()

while running:
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        elif evt.type == pygame.KEYDOWN:
            if not typingOptions.is_ctrl() and typingOptions.is_character_in_char_set(evt.key):
                text.add_character(typingOptions.get_character(evt.key), typingOptions.is_caps())
            elif evt.key == pygame.K_BACKSPACE: text.remove_character(True)
            elif evt.key == pygame.K_DELETE: text.remove_character(False)
            elif evt.key == pygame.K_CAPSLOCK or evt.key == pygame.K_LSHIFT or evt.key == pygame.K_RSHIFT: typingOptions.flip_caps()
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL : typingOptions.set_ctrl(True)
        elif evt.type == pygame.KEYUP:
            if evt.key == pygame.K_LSHIFT or evt.key == pygame.K_RSHIFT: typingOptions.flip_caps()
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL : typingOptions.set_ctrl(False)
                

    screen.fill(BLACK)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
