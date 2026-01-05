# ui/code_editor.py
import pygame

class CodeEditor:
    def __init__(self, font, line_height):
        self.font = font
        self.line_h = line_height

        self.lines = [""]
        self.cursor_line = 0
        self.cursor_col = 0
        self.scroll = 0

    def set_lines(self, lines):
        self.lines = lines
        self.cursor_line = len(lines) - 1
        self.cursor_col = len(lines[-1])
        self.scroll = 0

    def insert_line(self, text):
        self.lines.insert(self.cursor_line + 1, text)
        self.cursor_line += 1
        self.cursor_col = len(text)

    def handle_key(self, event):
        line = self.lines[self.cursor_line]

        if event.key == pygame.K_BACKSPACE:
            if self.cursor_col > 0:
                self.lines[self.cursor_line] = (
                    line[:self.cursor_col - 1] + line[self.cursor_col:]
                )
                self.cursor_col -= 1
            elif self.cursor_line > 0:
                prev = self.lines[self.cursor_line - 1]
                self.cursor_col = len(prev)
                self.lines[self.cursor_line - 1] = prev + line
                self.lines.pop(self.cursor_line)
                self.cursor_line -= 1

        elif event.key == pygame.K_RETURN:
            new = line[self.cursor_col:]
            self.lines[self.cursor_line] = line[:self.cursor_col]
            self.lines.insert(self.cursor_line + 1, new)
            self.cursor_line += 1
            self.cursor_col = 0

        elif event.unicode and event.unicode.isprintable():
            self.lines[self.cursor_line] = (
                line[:self.cursor_col] + event.unicode + line[self.cursor_col:]
            )
            self.cursor_col += 1
