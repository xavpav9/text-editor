import pygame, pyperclip

WHITE, BLACK, LIGHT_BLUE = (255,255,255), (0,0,0), (128,128,255)
FPS = 60

filename = ""
while filename == "" or filename == __file__.split("/")[-1]:
    filename = input("Enter a filename to edit/create: ")

pygame.init()

screen = pygame.display.set_mode((500, 700), pygame.RESIZABLE)
pygame.display.set_caption(f"Text Editor - {filename}")
clock = pygame.time.Clock()
current_frame = 0

class ScreenController:
    def __init__(self, screen):
        self.screen = screen
        self.scroll_top = 0
        self.padding_x = 20
        self.padding_y = 15
        self.set_font("Courier", 28, False, False)
        self.line_spacing = 12
        self.highlighting = False

    def set_font(self, typeface, size, bold, italics):
        if typeface != None: self.typeface = typeface
        if size != None: self.font_size = size
        if bold != None: self.bold = bold
        if italics != None: self.italics = italics

        self.font_size = min(75, max(4, self.font_size))

        self.font = pygame.font.SysFont(self.typeface, self.font_size, self.bold, self.italics)
        self.letter_width, self.letter_height = self.font.render("a", True, WHITE).get_size()

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
                        if len(current_line) > 0 or (j != 0 and word == ""): current_line += " " # space between words, unless newline, but not if newline and spaces
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
                if (i == len(new_lines) - 1 and highlighted_range[0] >= new_lines[i][0]) or (highlighted_range[0] >= new_lines[i][0] and highlighted_range[0] < new_lines[i+1][0]):
                    # either on last line and start is not reached, or not on last line, and start is on current line
                    self.highlighting = True

                if self.highlighting and highlighted_range[1] > new_lines[i][0]:
                    self.blit_line_to_screen(new_lines[i][1], i, False, blink, just_typed, max(0, highlighted_range[0] - new_lines[i][0]), min(len(new_lines[i][1]), highlighted_range[1] - new_lines[i][0]))
                else:
                    self.highlighting = False
                    self.blit_line_to_screen(new_lines[i][1], i, False, blink, just_typed)


                if i == cursor_position[0]:
                    line_to_compare = new_lines[i][1]
                    if i != len(new_lines) - 1 and new_lines[i][0] + chars_per_line - 1 == new_lines[i+1][0] and len(new_lines[i][1]) == chars_per_line:
                        # removes "-" if there is an overflow (detected using the current_text_pos and chars_per_line)
                        line_to_compare = new_lines[i][1][:-1]


                    if len(line_to_compare) == len(cursor_position[1]) and line_to_compare != new_lines[i][1]:
                        self.blit_line_to_screen("", i+1, True, blink, just_typed)
                    elif len(line_to_compare) >= len(cursor_position[1]):
                        self.blit_line_to_screen(cursor_position[1], i, True, blink, just_typed)
                    else:
                        if line_to_compare != new_lines[i][1]:
                            last_word = cursor_position[1].split(" ")[-1][chars_per_line - 1:]
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
        self.shifts = [False, False]
        self._ctrl = False
        self.blink = 0
        self.blink_period = 30
        self.holding = False
        self.recent_click = (0,0)
        self.current_letter = ""

        self.backspacing = -1
        self.deleting = -1
        self.maximising = -1
        self.minimising = -1
        self.typing = -1

    @property
    def ctrl(self):
        return self._ctrl

    @ctrl.setter
    def ctrl(self, boolean):
        self._ctrl = boolean
    
    def is_valid_char(self, letter):
        return ord(letter) >= 32 and ord(letter) <= 126

    def increment_blink(self):
        self.blink = (self.blink + 1) % (2 * self.blink_period)

    def reset_blink(self):
        self.blink = 0

    def get_blink_status(self):
        return self.blink < self.blink_period

    def increment_counter(self, counter_name):
        counter_value = 0
        match counter_name:
            case "backspace":
                counter_value = self.backspacing
                self.backspacing += 1
            case "delete":
                counter_value = self.deleting
                self.deleting += 1
            case "maximise":
                counter_value = self.maximising
                self.maximising += 1
            case "minimise":
                counter_value = self.minimising
                self.minimising += 1
            case "typing":
                counter_value = self.typing
                self.typing += 1
            case _:
                raise Exception("Invalid counter")

        if counter_value == 0 or (counter_value > 30 and counter_value % 3 == 0):
            return True
        return False


class Text:
    def __init__(self, initial_text=""):
        self.before_cursor = initial_text
        self.after_cursor = ""
        self.selected_range = [-1, -1]

    def add_character(self, letter):
        self.before_cursor += letter

    def remove_character(self, is_backspace):
        if self.before_cursor != "" and is_backspace: self.before_cursor = self.before_cursor[:-1]
        elif self.after_cursor != "" and not is_backspace: self.after_cursor = self.after_cursor[1:]

    def remove_word(self, is_backspace):
        if is_backspace:
            while self.before_cursor != "" and self.before_cursor[-1] != " " and self.before_cursor[-1] != "\n":
                self.before_cursor = self.before_cursor[:-1]
            if self.before_cursor != "": self.before_cursor = self.before_cursor[:-1]
        elif not is_backspace:
            while self.after_cursor != "" and self.after_cursor[0] != " " and self.after_cursor[0] != "\n":
                self.after_cursor = self.after_cursor[1:]
            if self.after_cursor != "": self.after_cursor = self.after_cursor[1:]

    def remove_selected(self):
        if self.selected_range[0] != -1:
            full_text = self.before_cursor + self.after_cursor
            self.before_cursor = full_text[:self.selected_range[0]]
            self.after_cursor = full_text[self.selected_range[1]:]
            self.selected_range = [-1, -1]

class FileHandler:
    def __init__(self, filename):
        if not self.check_file_exists(filename): open(filename, "x")
        self.filename = filename

    def check_file_exists(self, filename):
        try:
            open(filename, "r")
        except:
            return False
        return True

    def write_to_file(self, text):
        pygame.display.set_caption(f"Text Editor - {self.filename} (Saved)")
        file = open(self.filename, "w")
        file.write(text)
        file.close()

    def read_file(self):
        file = open(self.filename, "r")
        text = file.read()
        file.close()
        return text


running = True
fileHandler = FileHandler(filename)
typingOptions = TypingOptions()
text = Text(fileHandler.read_file())
screenController = ScreenController(screen)

while running:
    just_typed = False
    for evt in pygame.event.get():
        if evt.type == pygame.QUIT:
            running = False
        elif evt.type == pygame.KEYDOWN:
            typingOptions.reset_blink()
            if not typingOptions.ctrl and evt.unicode != "" and typingOptions.is_valid_char(evt.unicode):
                text.remove_selected()
                typingOptions.typing = 0
                typingOptions.current_letter = evt.unicode
            elif evt.key == pygame.K_RETURN and not typingOptions.ctrl:
                text.remove_selected()
                typingOptions.typing = 0
                typingOptions.current_letter = "\n"
            elif evt.key == pygame.K_BACKSPACE: typingOptions.increment_counter("backspace")
            elif evt.key == pygame.K_DELETE: typingOptions.increment_counter("delete")
            elif evt.key == pygame.K_LSHIFT: typingOptions.shifts[0] = True
            elif evt.key == pygame.K_RSHIFT: typingOptions.shifts[1] = True
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL: typingOptions.ctrl = True
            elif evt.key == pygame.K_c and typingOptions.ctrl: pyperclip.copy(f"{text.before_cursor}{text.after_cursor}"[text.selected_range[0]:text.selected_range[1]])
            elif evt.key == pygame.K_v and typingOptions.ctrl: text.before_cursor += pyperclip.paste()
            elif evt.unicode == "+" and typingOptions.ctrl: typingOptions.increment_counter("maximise")
            elif evt.key == pygame.K_MINUS and typingOptions.ctrl: typingOptions.increment_counter("minimise")
            elif evt.key == pygame.K_b and typingOptions.ctrl: screenController.set_font(None, None, not screenController.bold, None)
            elif evt.key == pygame.K_i and typingOptions.ctrl: screenController.set_font(None, None, None, not screenController.italics)
            elif evt.key == pygame.K_s and typingOptions.ctrl: fileHandler.write_to_file(text.before_cursor + text.after_cursor)
        elif evt.type == pygame.KEYUP:
            if evt.unicode != "" and typingOptions.is_valid_char(evt.unicode):
                if typingOptions.current_letter == evt.unicode:
                    typingOptions.typing = -1
                    typingOptions.current_letter = ""
            elif evt.key == pygame.K_RETURN:
                if typingOptions.current_letter == "\n":
                    typingOptions.typing = -1
                    typingOptions.current_letter = ""
            elif evt.key == pygame.K_LSHIFT: typingOptions.shifts[0] = False
            elif evt.key == pygame.K_RSHIFT: typingOptions.shifts[1] = False
            elif evt.key == pygame.K_LCTRL or evt.key == pygame.K_RCTRL: typingOptions.ctrl = False
            elif evt.key == pygame.K_BACKSPACE: typingOptions.backspacing = -1
            elif evt.key == pygame.K_DELETE: typingOptions.deleting = -1
            elif evt.unicode == "+": typingOptions.maximising = -1
            elif evt.key == pygame.K_MINUS: typingOptions.minimising = -1
        elif evt.type == pygame.MOUSEWHEEL:
            screenController.scroll_top = min(0, screenController.scroll_top + (evt.y * 8))
        elif evt.type == pygame.MOUSEBUTTONDOWN:
            if evt.button == 1:
                typingOptions.holding = True
                typingOptions.recent_click = pygame.mouse.get_pos()
                text.before_cursor, text.after_cursor, _ = screenController.get_new_text_positions(pygame.mouse.get_pos(), text.before_cursor, text.after_cursor)
        elif evt.type == pygame.MOUSEBUTTONUP:
            if evt.button == 1: typingOptions.holding = False

                

    screen.fill(BLACK)
    typingOptions.increment_blink()
    if typingOptions.backspacing != -1:
        if typingOptions.increment_counter("backspace"):
            if text.selected_range[0] != -1: text.remove_selected()
            elif not typingOptions.ctrl: text.remove_character(True)
            else: text.remove_word(True);
    if typingOptions.deleting != -1:
        if typingOptions.increment_counter("delete"):
            if text.selected_range[0] != -1: text.remove_selected()
            elif not typingOptions.ctrl: text.remove_character(False)
            else: text.remove_word(False);
    if typingOptions.holding:
        text.before_cursor, text.after_cursor, line = screenController.get_new_text_positions(pygame.mouse.get_pos(), text.before_cursor, text.after_cursor)
        text.selected_range = screenController.get_selected_text(typingOptions.recent_click, pygame.mouse.get_pos(), text.before_cursor, text.after_cursor)
        
        y_pos = screenController.get_y_of_line(screenController.get_line_number(pygame.mouse.get_pos()[1]))

        if current_frame % FPS % 5 == 0:
            screenController.adjust_scroll_top(y_pos + 0.1)
            screenController.adjust_scroll_top(y_pos - 0.1)

    if typingOptions.maximising != -1:
        if typingOptions.increment_counter("maximise"): screenController.set_font(None, screenController.font_size + 2, None, None)
    if typingOptions.minimising != -1:
        if typingOptions.increment_counter("minimise"): screenController.set_font(None, screenController.font_size - 2, None, None)
    if typingOptions.typing != -1:
        if typingOptions.increment_counter("typing"): text.add_character(typingOptions.current_letter)

    if typingOptions.typing != -1 or typingOptions.maximising != -1 or typingOptions.minimising != -1 or typingOptions.holding or typingOptions.backspacing != -1 or typingOptions.deleting != -1:
        typingOptions.reset_blink()
        just_typed = True

    screenController.draw_text(True, text.before_cursor, text.after_cursor, typingOptions.get_blink_status(), just_typed, text.selected_range)

    if just_typed:
        pygame.display.set_caption(f"Text Editor - {filename} (Unsaved)")

    pygame.display.flip()
    current_frame += 1
    clock.tick(FPS)

pygame.quit()
