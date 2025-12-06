import pygame, pyperclip

pygame.init()

WHITE, BLACK, LIGHT_BLUE = (255,255,255), (0,0,0), (128,128,255)

screen = pygame.display.set_mode((400, 200))
pygame.display.set_caption("Text Editor")
clock = pygame.time.Clock()
current_frame = 0

class ScreenController:
    def __init__(self, screen):
        self.screen = screen
        self.scroll_top = 0
        self.padding_x = 20
        self.padding_y = 15
        self.font = pygame.font.SysFont("Courier", 28, False, False)
        self.letter_width, self.letter_height = self.font.render("a", True, WHITE).get_size()
        self.line_spacing = 12
        self.highlighting = False

    def get_line_number(self, mouse_y):
        line_number = 0
        while mouse_y > self.scroll_top + self.padding_y + (self.letter_height + self.line_spacing) * line_number:
            line_number += 1
        return line_number - 1

    def get_y_of_line(self, line_number):
        return self.scroll_top + self.padding_y + (self.letter_height + self.line_spacing) * line_number

    def adjust_scroll_top(self, y, just_typed=True):
        if y < 0 and just_typed:
            self.scroll_top += (self.line_spacing - y)
        elif y + self.letter_height + self.line_spacing > screen.get_size()[1] and just_typed:
            self.scroll_top -= (y + self.letter_height + self.line_spacing - screen.get_size()[1])
        self.scroll_top = min(0, self.scroll_top)

    def blit_line_to_screen(self, text, line_number, cursor, blink=False, just_typed=False, start_highlight=0, end_highlight=-1):
        coords = (self.padding_x / 2, self.get_y_of_line(line_number))
        if cursor:
            if blink: pygame.draw.rect(screen, WHITE, (coords[0] + len(text) * self.letter_width, coords[1], 2, self.letter_height))
            self.adjust_scroll_top(coords[1], just_typed)
        elif self.highlighting:
            pygame.draw.rect(screen, LIGHT_BLUE, (coords[0] + start_highlight * self.letter_width, coords[1], (end_highlight - start_highlight) * self.letter_width, self.letter_height))
            self.screen.blit(self.font.render(text, True, WHITE), coords)
        else: self.screen.blit(self.font.render(text, True, WHITE), coords)
        return coords

    def format_lines(self, lines, current_text_pos, chars_per_line):
        new_lines = []
        current_line = ""
        if len(lines) != 1 or lines[0] != "":
            for o in range(len(lines)):
                for j in range(len(lines[o].split(" "))):
                    word = lines[o].split(" ")[j]
                    if len(current_line + word) > chars_per_line and current_line != "":
                        new_lines.append([current_text_pos, current_line])
                        current_text_pos += len(current_line)
                        current_text_pos += 1 # to account for spaces
                        current_line = ""

                    if len(word) > chars_per_line:
                        current_line = ""
                        for i in range(len(word)):
                            if len(current_line + word[i]) == chars_per_line and i != len(word) - 1:
                                new_lines.append([current_text_pos, current_line + "-"])
                                current_text_pos += len(current_line)
                                current_line = ""
                            current_line += word[i]

                    else:
                        if len(current_line) > 0: current_line += " "
                        current_line += word

                if o != len(lines) - 1:
                    new_lines.append([current_text_pos, current_line])
                    current_text_pos += len(current_line) + 1 # to account for newlines
                    current_line = ""

        return new_lines, current_line, current_text_pos

    def draw_text(self, draw, text_before_cursor, text_after_cursor, blink, just_typed, highlighted_range=[-1,-1]):
        chars_per_line = (self.screen.get_size()[0] - self.padding_x) // self.letter_width - 1
        current_text_pos = 0
        new_lines = []
        formatted_lines = []
        current_line = ""
        cursor_position = [0, ""] # format: [line number, line]

        if text_before_cursor != "":
            lines = text_before_cursor.split("\n")
            formatted_lines, current_line, current_text_pos = self.format_lines(lines, current_text_pos, chars_per_line)
            if len(formatted_lines) > 0:
                for line in formatted_lines: new_lines.append(line)

            cursor_position = [len(new_lines), current_line]

        if text_after_cursor != "":
            lines = text_after_cursor.split("\n")
            if len(lines) != 0: lines[0] = current_line + lines[0]
            else: lines.append(current_line)
            formatted_lines, current_line, current_text_pos = self.format_lines(lines, current_text_pos, chars_per_line)
            formatted_lines.append([current_text_pos, current_line])
            for line in formatted_lines: new_lines.append(line)
        else:
            new_lines.append([current_text_pos, current_line])

        if draw:
            for i in range(len(new_lines)):
                if highlighted_range[0] >= new_lines[i][0]: self.highlighting = True

                if self.highlighting and highlighted_range[1] > new_lines[i][0]:
                    self.blit_line_to_screen(new_lines[i][1], i, False, blink, just_typed, max(0, highlighted_range[0] - new_lines[i][0]), min(len(new_lines[i][1]), highlighted_range[1] - new_lines[i][0]))
                else:
                    self.highlighting = False
                    self.blit_line_to_screen(new_lines[i][1], i, False, blink, just_typed)

                if i == cursor_position[0]:
                    if len(new_lines[i][1]) >= len(cursor_position[1]):
                        self.blit_line_to_screen(cursor_position[1], i, True, blink, just_typed)
                    else:
                        last_word = cursor_position[1].split(" ")[-1]
                        self.blit_line_to_screen(last_word, i + 1, True, blink, just_typed)

            self.highlighting = False

        return new_lines

    def get_new_text_positions(self, mouse_pos, text_before_cursor, text_after_cursor):
        line_number = self.get_line_number(mouse_pos[1])

        x_index = max(0, (mouse_pos[0] - self.padding_x / 2) // self.letter_width)

        formatted_lines = self.draw_text(False, text_before_cursor, text_after_cursor, False, False)

        if line_number < len(formatted_lines):
            full_text = text_before_cursor + text_after_cursor
            current_text_pos = formatted_lines[line_number][0]
            line_length = len(formatted_lines[line_number][1])
            distance_across = int(current_text_pos + min(line_length, x_index))
            return full_text[:distance_across], full_text[distance_across:], formatted_lines[line_number][1]
        else:
            return text_before_cursor + text_after_cursor, "", ""

    def get_selected_text(self, cursor_pos, mouse_pos, new_text_before, new_text_after):
        old_text_before, old_text_after, line = self.get_new_text_positions(cursor_pos, new_text_before, new_text_after)
        chars_per_line = (self.screen.get_size()[0] - self.padding_x) // self.letter_width - 1
        full_text = new_text_before + new_text_after

        if len(new_text_before) >= len(old_text_before):
            if " " not in line and len(line) == chars_per_line and cursor_pos[0] > (chars_per_line) * self.letter_width + self.padding_x / 2:
                start_pos, end_pos = len(old_text_before), len(new_text_before) - 1
                # for when there is only one word, do not interpret the hyphen as the next letter
            else: start_pos, end_pos = len(old_text_before), len(new_text_before)
        else:
            if cursor_pos[0] <= self.padding_x / 2: start_pos, end_pos = len(full_text) - len(new_text_after), len(old_text_before)
                # for when the mouse is out of the editable screen, select the first letter of the line
            else: start_pos, end_pos = len(full_text) - len(new_text_after), len(old_text_before)

        return start_pos, end_pos



class TypingOptions:
    def __init__(self):
        self._caps = False
        self._ctrl = False
        self.char_map = { pygame.K_SPACE: " ", pygame.K_EXCLAIM: "!", pygame.K_QUOTEDBL: "\"", pygame.K_HASH: "#", pygame.K_DOLLAR: "$", pygame.K_AMPERSAND: "&", pygame.K_QUOTE: "'", pygame.K_LEFTPAREN: "(", pygame.K_RIGHTPAREN: ")", pygame.K_ASTERISK: "*", pygame.K_PLUS: "+", pygame.K_COMMA: ",", pygame.K_MINUS: "-", pygame.K_PERIOD: ".", pygame.K_SLASH: "/", pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3", pygame.K_4: "4", pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8", pygame.K_9: "9", pygame.K_COLON: ":", pygame.K_SEMICOLON: ";", pygame.K_LESS: "<", pygame.K_EQUALS: "=", pygame.K_GREATER: ">", pygame.K_QUESTION: "?", pygame.K_AT: "@", pygame.K_LEFTBRACKET: "[", pygame.K_BACKSLASH: "\\", pygame.K_RIGHTBRACKET: "]", pygame.K_CARET: "^", pygame.K_UNDERSCORE: "_", pygame.K_BACKQUOTE: "`", pygame.K_a: "a", pygame.K_b: "b", pygame.K_c: "c", pygame.K_d: "d", pygame.K_e: "e", pygame.K_f: "f", pygame.K_g: "g", pygame.K_h: "h", pygame.K_i: "i", pygame.K_j: "j", pygame.K_k: "k", pygame.K_l: "l", pygame.K_m: "m", pygame.K_n: "n", pygame.K_o: "o", pygame.K_p: "p", pygame.K_q: "q", pygame.K_r: "r", pygame.K_s: "s", pygame.K_t: "t", pygame.K_u: "u", pygame.K_v: "v", pygame.K_w: "w", pygame.K_x: "x", pygame.K_y: "y", pygame.K_z: "z", pygame.K_KP_DIVIDE: "/", pygame.K_KP_MULTIPLY: "*", pygame.K_KP_MINUS: "-", pygame.K_KP_PLUS: "+", pygame.K_KP_EQUALS: "=", pygame.K_RETURN: "\n"}
        self.blink = 0
        self.blink_period = 30
        self.backspacing = -1
        self.deleting = -1
        self.holding = False
        self.recent_click = (0,0)

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
        self.selected_range = [-1, -1]

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
    def remove_selected(self):
        if self.selected_range[0] != -1:
            full_text = self.before_cursor + self.after_cursor
            self.before_cursor = full_text[:self.selected_range[0]]
            self.after_cursor = full_text[self.selected_range[1]:]
            self.selected_range = [-1, -1]

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
                text.remove_selected()
                just_typed = True
                text.add_character(typingOptions.get_character(evt.key), typingOptions.caps)
            elif evt.key == pygame.K_BACKSPACE: typingOptions.increment_and_backspace()
            elif evt.key == pygame.K_DELETE: typingOptions.increment_and_delete()
            elif evt.key == pygame.K_CAPSLOCK or evt.key == pygame.K_LSHIFT or evt.key == pygame.K_RSHIFT: typingOptions.flip_caps()
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL: typingOptions.ctrl = True
            elif evt.key == pygame.K_c and typingOptions.ctrl: pyperclip.copy(f"{text.before_cursor}{text.after_cursor}"[text.selected_range[0]:text.selected_range[1]])
            elif evt.key == pygame.K_v and typingOptions.ctrl: text.before_cursor += pyperclip.paste()
        elif evt.type == pygame.KEYUP:
            if evt.key == pygame.K_LSHIFT or evt.key == pygame.K_RSHIFT: typingOptions.flip_caps()
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL : typingOptions.ctrl = False
            elif evt.key == pygame.K_BACKSPACE: typingOptions.backspacing = -1
            elif evt.key == pygame.K_DELETE: typingOptions.deleting = -1
        elif evt.type == pygame.MOUSEWHEEL:
            screenController.scroll_top = min(0, screenController.scroll_top + (evt.y * 8))
        elif evt.type == pygame.MOUSEBUTTONDOWN:
            if evt.button == 1:
                typingOptions.holding = True
                typingOptions.recent_click = pygame.mouse.get_pos()
                text.before_cursor, text.after_cursor, _ = screenController.get_new_text_positions(pygame.mouse.get_pos(), text.before_cursor, text.after_cursor)
                typingOptions.reset_blink()
        elif evt.type == pygame.MOUSEBUTTONUP:
            if evt.button == 1: typingOptions.holding = False

                

    screen.fill(BLACK)
    typingOptions.increment_blink()
    if typingOptions.backspacing != -1:
        if typingOptions.increment_and_backspace():
            if text.selected_range[0] != -1: text.remove_selected()
            elif not typingOptions.ctrl: text.remove_character(True)
            else: text.remove_word(True);
    if typingOptions.deleting != -1:
        if typingOptions.increment_and_delete():
            if text.selected_range[0] != -1: text.remove_selected()
            elif not typingOptions.ctrl: text.remove_character(False)
            else: text.remove_word(False);
    if typingOptions.holding:
        text.before_cursor, text.after_cursor, line = screenController.get_new_text_positions(pygame.mouse.get_pos(), text.before_cursor, text.after_cursor)
        text.selected_range = screenController.get_selected_text(typingOptions.recent_click, pygame.mouse.get_pos(), text.before_cursor, text.after_cursor)
        
        y_pos = screenController.get_y_of_line(screenController.get_line_number(pygame.mouse.get_pos()[1]))

        if current_frame % 60 % 5 == 0:
            screenController.adjust_scroll_top(y_pos + 0.1)
            screenController.adjust_scroll_top(y_pos - 0.1)

    screenController.draw_text(True, text.before_cursor, text.after_cursor, typingOptions.get_blink_status(), just_typed, text.selected_range)

    pygame.display.flip()
    current_frame += 1
    clock.tick(60)

pygame.quit()
