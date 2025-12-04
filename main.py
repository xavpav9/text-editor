import pygame

pygame.init()

WHITE, BLACK = (255,255,255), (0,0,0)

screen = pygame.display.set_mode((400, 200))
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

    def blit_line_to_screen(self, text, line_number, cursor, blink=False, just_typed=False):
        coords = (self.padding_x / 2, self.scroll_top + self.padding_y + (self.letter_height + self.line_spacing) * line_number)
        if cursor:
            if blink: pygame.draw.rect(screen, WHITE, (coords[0] + len(text) * self.letter_width, coords[1], 2, self.letter_height))
            if coords[1] < 0 and just_typed:
                self.scroll_top +=  (self.line_spacing - coords[1])
            elif coords[1] + self.letter_height + self.line_spacing > screen.get_size()[1] and just_typed:
                self.scroll_top -= (coords[1] + self.letter_height + self.line_spacing - screen.get_size()[1])
            self.scroll_top = min(0, self.scroll_top)
        elif not cursor: self.screen.blit(self.font.render(text, True, WHITE), coords)
        return coords

    def blit_words_to_screen(self, lines, line_number, chars_per_line, current_text_pos, mouse_line):
        text_to_be_blitted = ""
        if len(lines) != 1 or lines[0] != "":
            for o in range(len(lines)):
                line = lines[o]
                for word in line.split(" "):
                    if len(text_to_be_blitted + word) > chars_per_line and text_to_be_blitted != "":
                        if line_number == mouse_line: return text_to_be_blitted, mouse_line, current_text_pos
                        current_text_pos += len(text_to_be_blitted)
                        self.blit_line_to_screen(text_to_be_blitted, line_number, False)
                        text_to_be_blitted = ""
                        line_number += 1

                    if len(word) > chars_per_line:
                        text_to_be_blitted = ""
                        for i in range(len(word)):
                            letter = word[i]
                            if len(text_to_be_blitted + letter) == chars_per_line and i != len(word) - 1:
                                if line_number == mouse_line: return text_to_be_blitted, mouse_line, current_text_pos
                                current_text_pos += len(text_to_be_blitted)
                                self.blit_line_to_screen(text_to_be_blitted + "-", line_number, False)
                                line_number += 1
                                text_to_be_blitted = ""
                            text_to_be_blitted += letter

                        text_to_be_blitted += " "
                    else:
                        text_to_be_blitted += word + " "

                if o != len(lines) - 1:
                    text_to_be_blitted = text_to_be_blitted[:-1]
                    if line_number == mouse_line: return text_to_be_blitted, mouse_line, current_text_pos
                    current_text_pos += len(text_to_be_blitted)
                    self.blit_line_to_screen(text_to_be_blitted, line_number, False)
                    text_to_be_blitted = ""
                    line_number += 1

        return text_to_be_blitted, line_number, current_text_pos

    def draw_text(self, text_before_cursor, text_after_cursor, blink, just_typed, mouse_line=-1):
        chars_per_line = (self.screen.get_size()[0] - self.padding_x) // self.letter_width
        line_number = 0
        current_text_pos = 0

        if text_before_cursor == "" and text_after_cursor == "":
            self.blit_line_to_screen("", line_number, True, blink)
            return

        lines = text_before_cursor.split("\n")
        text_to_be_blitted, line_number, current_text_pos = self.blit_words_to_screen(lines, line_number, chars_per_line, current_text_pos, mouse_line)
        if mouse_line == line_number: return current_text_pos

        text_to_be_blitted = text_to_be_blitted[:-1]
        if text_after_cursor != "":
            last_space = 0
            for i in range(len(text_to_be_blitted)):
                if text_to_be_blitted[i] == " ":
                    last_space = i

            last_word = text_to_be_blitted[last_space:]
            first_word = text_after_cursor.split("\n")[0].split(" ")[0]
            overflowing = len(text_to_be_blitted + first_word) / chars_per_line > 1

            if overflowing:
                self.blit_line_to_screen(" " * (len(last_word) - 1), line_number + 1, True, blink, just_typed)
            else:
                self.blit_line_to_screen(text_to_be_blitted, line_number, True, blink, just_typed)
        else:
            self.blit_line_to_screen(text_to_be_blitted, line_number, True, blink, just_typed)

        lines = text_after_cursor.split("\n")
        if len(lines) != 0: lines[0] = text_to_be_blitted + lines[0]
        else: lines.append(text_to_be_blitted)
        text_to_be_blitted, line_number, current_text_pos = self.blit_words_to_screen(lines, line_number, chars_per_line, current_text_pos, mouse_line)
        if mouse_line == line_number: return current_text_pos

        self.blit_line_to_screen(text_to_be_blitted[:-1], line_number, False)

        return -1, 0

    def get_character_from_pos(self, mouse_pos, text_before_cursor, text_after_cursor):
        line_number = 0
        while mouse_pos[1] > self.scroll_top + self.padding_y + (self.letter_height + self.line_spacing) * line_number:
            line_number += 1
        line_number -= 1

        x_index = (mouse_pos[0] - self.padding_x / 2) // self.letter_width

        current_text_pos = self.draw_text(text_before_cursor, text_after_cursor, False, False, line_number)
        # current_text_pos is the pos of that start of the line
        if current_text_pos == -1:
            return text_before_cursor + text_after_cursor, ""

        full_text = text_before_cursor + text_after_cursor
        return full_text[:int(current_text_pos + x_index)], full_text[int(current_text_pos + x_index):]


class TypingOptions:
    def __init__(self):
        self._caps = False
        self._ctrl = False
        self.char_map = { pygame.K_SPACE: " ", pygame.K_EXCLAIM: "!", pygame.K_QUOTEDBL: "\"", pygame.K_HASH: "#", pygame.K_DOLLAR: "$", pygame.K_AMPERSAND: "&", pygame.K_QUOTE: "'", pygame.K_LEFTPAREN: "(", pygame.K_RIGHTPAREN: ")", pygame.K_ASTERISK: "*", pygame.K_PLUS: "+", pygame.K_COMMA: ",", pygame.K_MINUS: "-", pygame.K_PERIOD: ".", pygame.K_SLASH: "/", pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3", pygame.K_4: "4", pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8", pygame.K_9: "9", pygame.K_COLON: ":", pygame.K_SEMICOLON: ";", pygame.K_LESS: "<", pygame.K_EQUALS: "=", pygame.K_GREATER: ">", pygame.K_QUESTION: "?", pygame.K_AT: "@", pygame.K_LEFTBRACKET: "[", pygame.K_BACKSLASH: "\\", pygame.K_RIGHTBRACKET: "]", pygame.K_CARET: "^", pygame.K_UNDERSCORE: "_", pygame.K_BACKQUOTE: "`", pygame.K_a: "a", pygame.K_b: "b", pygame.K_c: "c", pygame.K_d: "d", pygame.K_e: "e", pygame.K_f: "f", pygame.K_g: "g", pygame.K_h: "h", pygame.K_i: "i", pygame.K_j: "j", pygame.K_k: "k", pygame.K_l: "l", pygame.K_m: "m", pygame.K_n: "n", pygame.K_o: "o", pygame.K_p: "p", pygame.K_q: "q", pygame.K_r: "r", pygame.K_s: "s", pygame.K_t: "t", pygame.K_u: "u", pygame.K_v: "v", pygame.K_w: "w", pygame.K_x: "x", pygame.K_y: "y", pygame.K_z: "z", pygame.K_KP_DIVIDE: "/", pygame.K_KP_MULTIPLY: "*", pygame.K_KP_MINUS: "-", pygame.K_KP_PLUS: "+", pygame.K_KP_EQUALS: "=", pygame.K_RETURN: "\n"}
        self.blink = 0
        self.blink_period = 30
        self.backspacing = -1
        self.deleting = -1

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

    def increment_and_backspace(self):
        backspace = False
        if self.backspacing == 0 or (self.backspacing > 30 and self.backspacing % 3 == 0):
            backspace = True
        self.backspacing += 1
        return backspace

    def increment_and_delete(self):
        delete = False
        if self.deleting == 0 or (self.deleting > 30 and self.deleting % 3 == 0):
            delete = True
        self.deleting += 1
        return delete


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

    def remove_word(self, is_backspace):
        if is_backspace:
            while self.before_cursor != "" and self.before_cursor[-1] != " ":
                self.before_cursor = self.before_cursor[:-1]
            if self.before_cursor != "": self.before_cursor = self.before_cursor[:-1]
        elif not is_backspace:
            #to fix
            while self.after_cursor != "" and self.after_cursor[0] != " ":
                self.after_cursor = self.after_cursor[1:]
            if self.after_cursor != "": self.after_cursor = self.after_cursor[1:]

running = True
typingOptions = TypingOptions()
text = Text()
screenController = ScreenController(screen)

while running:
    just_typed = False
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        elif evt.type == pygame.KEYDOWN:
            typingOptions.reset_blink()
            if not typingOptions.ctrl and typingOptions.is_character_in_char_set(evt.key):
                just_typed = True
                text.add_character(typingOptions.get_character(evt.key), typingOptions.caps)
            elif evt.key == pygame.K_BACKSPACE: typingOptions.increment_and_backspace()
            elif evt.key == pygame.K_DELETE: typingOptions.increment_and_delete()
            elif evt.key == pygame.K_CAPSLOCK or evt.key == pygame.K_LSHIFT or evt.key == pygame.K_RSHIFT: typingOptions.flip_caps()
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL : typingOptions.ctrl = True
        elif evt.type == pygame.KEYUP:
            if evt.key == pygame.K_LSHIFT or evt.key == pygame.K_RSHIFT: typingOptions.flip_caps()
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL : typingOptions.ctrl = False
            elif evt.key == pygame.K_BACKSPACE: typingOptions.backspacing = -1
            elif evt.key == pygame.K_DELETE: typingOptions.deleting = -1
        elif evt.type == pygame.MOUSEWHEEL:
            screenController.scroll_top = min(0, screenController.scroll_top + (evt.y * 8))
        elif evt.type == pygame.MOUSEBUTTONDOWN:
            if evt.button == 1: text.before_cursor, text.after_cursor = screenController.get_character_from_pos(pygame.mouse.get_pos(), text.before_cursor, text.after_cursor)
                

    screen.fill(BLACK)
    typingOptions.increment_blink()
    if typingOptions.backspacing != -1:
        if typingOptions.increment_and_backspace():
            if not typingOptions.ctrl: text.remove_character(True)
            else: text.remove_word(True);
    if typingOptions.deleting != -1:
        if typingOptions.increment_and_delete():
            if not typingOptions.ctrl: text.remove_character(False)
            else: text.remove_word(False);

    screenController.draw_text(text.before_cursor, text.after_cursor, typingOptions.get_blink_status(), just_typed)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
