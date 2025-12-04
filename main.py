import pygame

pygame.init()

WHITE, BLACK = (255,255,255), (0,0,0)

screen = pygame.display.set_mode((400, 500))
pygame.display.set_caption("Text Editor")
clock = pygame.time.Clock()

class ScreenController:
    def __init__(self, screen):
        self.screen = screen
        self.scroll_top = 0
        self.padding_x = 20
        self.padding_y = 15
        self.font = pygame.font.SysFont("Courier", 28, False, False)
        self.letter_width, self.letter_height = self.font.render("a", True, WHITE).get_size()
        self.line_spacing = 12

    def blit_line_to_screen(self, text, line, cursor, blink=False):
        coords = (self.padding_x / 2, self.padding_y + (self.letter_height + self.line_spacing) * line)
        if cursor and blink: pygame.draw.rect(screen, WHITE, (coords[0] + len(text) * self.letter_width, coords[1], 2, self.letter_height))
        elif not cursor: self.screen.blit(self.font.render(text, True, WHITE), coords)
        return coords

    def blit_words_to_screen(self, words, line, chars_per_line):
        text_to_be_blitted = ""
        if len(words) != 1 or words[0] != "":
            for word in words:
                if len(text_to_be_blitted + word) > chars_per_line and text_to_be_blitted != "":
                    previous_line_coords = self.blit_line_to_screen(text_to_be_blitted, line, False)
                    text_to_be_blitted = ""
                    line += 1

                if len(word) > chars_per_line:
                    text_to_be_blitted = ""
                    for i in range(len(word)):
                        letter = word[i]
                        if len(text_to_be_blitted + letter) == chars_per_line and i != len(word) - 1:
                            self.blit_line_to_screen(text_to_be_blitted + "-", line, False)
                            line += 1
                            text_to_be_blitted = ""
                        text_to_be_blitted += letter

                    text_to_be_blitted += " "
                else:
                    text_to_be_blitted += word + " "

        if len(text_to_be_blitted) - 1 == chars_per_line:
            self.blit_line_to_screen(text_to_be_blitted + "", line, False)
            line += 1
            text_to_be_blitted = ""

        return text_to_be_blitted, line

    def draw_text(self, text_before_cursor, text_after_cursor, blink):
        chars_per_line = (self.screen.get_size()[0] - self.padding_x) // self.letter_width
        line = 0

        if text_before_cursor == "" and text_after_cursor == "":
            self.blit_line_to_screen("", line, True and blink)
            return

        words = text_before_cursor.split(" ")
        text_to_be_blitted, line = self.blit_words_to_screen(words, line, chars_per_line)

        self.blit_line_to_screen(text_to_be_blitted[:-1], line, True, blink)

        words = [text_to_be_blitted] + text_after_cursor.split(" ")
        text_to_be_blitted, line = self.blit_words_to_screen(words, line, chars_per_line)

        self.blit_line_to_screen(text_to_be_blitted[:-1], line, False)


class TypingOptions:
    def __init__(self):
        self._caps = False
        self._ctrl = False
        self.char_map = { pygame.K_SPACE: " ", pygame.K_EXCLAIM: "!", pygame.K_QUOTEDBL: "\"", pygame.K_HASH: "#", pygame.K_DOLLAR: "$", pygame.K_AMPERSAND: "&", pygame.K_QUOTE: "'", pygame.K_LEFTPAREN: "(", pygame.K_RIGHTPAREN: ")", pygame.K_ASTERISK: "*", pygame.K_PLUS: "+", pygame.K_COMMA: ",", pygame.K_MINUS: "-", pygame.K_PERIOD: ".", pygame.K_SLASH: "/", pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3", pygame.K_4: "4", pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8", pygame.K_9: "9", pygame.K_COLON: ":", pygame.K_SEMICOLON: ";", pygame.K_LESS: "<", pygame.K_EQUALS: "=", pygame.K_GREATER: ">", pygame.K_QUESTION: "?", pygame.K_AT: "@", pygame.K_LEFTBRACKET: "[", pygame.K_BACKSLASH: "\\", pygame.K_RIGHTBRACKET: "]", pygame.K_CARET: "^", pygame.K_UNDERSCORE: "_", pygame.K_BACKQUOTE: "`", pygame.K_a: "a", pygame.K_b: "b", pygame.K_c: "c", pygame.K_d: "d", pygame.K_e: "e", pygame.K_f: "f", pygame.K_g: "g", pygame.K_h: "h", pygame.K_i: "i", pygame.K_j: "j", pygame.K_k: "k", pygame.K_l: "l", pygame.K_m: "m", pygame.K_n: "n", pygame.K_o: "o", pygame.K_p: "p", pygame.K_q: "q", pygame.K_r: "r", pygame.K_s: "s", pygame.K_t: "t", pygame.K_u: "u", pygame.K_v: "v", pygame.K_w: "w", pygame.K_x: "x", pygame.K_y: "y", pygame.K_z: "z", pygame.K_KP_DIVIDE: "/", pygame.K_KP_MULTIPLY: "*", pygame.K_KP_MINUS: "-", pygame.K_KP_PLUS: "+", pygame.K_KP_EQUALS: "=", }
        self.blink = 0
        self.blink_period = 30

    @property
    def ctrl(self):
        return self._ctrl

    @ctrl.setter
    def ctrl(self, boolean):
        self._ctrl = boolean
    
    def is_character_in_char_set(self, letter):
        return letter in self.char_map

    def get_character(self, keypress):
        return self.char_map[keypress]

    @property
    def caps(self):
        return self._caps

    def flip_caps(self):
        self._caps = not self._caps

    def increment_blink(self):
        self.blink = (self.blink + 1) % (2 * self.blink_period)

    def reset_blink(self):
        self.blink = 0

    def get_blink_status(self):
        return self.blink < self.blink_period

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
screenController = ScreenController(screen)

while running:
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        elif evt.type == pygame.KEYDOWN:
            typingOptions.reset_blink()
            if not typingOptions.ctrl and typingOptions.is_character_in_char_set(evt.key):
                text.add_character(typingOptions.get_character(evt.key), typingOptions.caps)
            elif evt.key == pygame.K_BACKSPACE: text.remove_character(True)
            elif evt.key == pygame.K_DELETE: text.remove_character(False)
            elif evt.key == pygame.K_CAPSLOCK or evt.key == pygame.K_LSHIFT or evt.key == pygame.K_RSHIFT: typingOptions.flip_caps()
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL : typingOptions.ctrl = True
        elif evt.type == pygame.KEYUP:
            if evt.key == pygame.K_LSHIFT or evt.key == pygame.K_RSHIFT: typingOptions.flip_caps()
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL : typingOptions.ctrl = False
                

    screen.fill(BLACK)
    typingOptions.increment_blink()

    screenController.draw_text(text.before_cursor, text.after_cursor, typingOptions.get_blink_status())

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
