# ui/ui_text.py

class UITextLayout:
    def __init__(self, font, line_height=18):
        self.font = font
        self.line_height = line_height

    def wrap_words(self, text, max_width):
        words = text.split(" ")
        lines = []
        current = ""

        for word in words:
            test = word if not current else current + " " + word
            if self.font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                    current = word
                else:
                    # fallback: từ quá dài
                    cut = ""
                    for ch in word:
                        if self.font.size(cut + ch)[0] <= max_width:
                            cut += ch
                        else:
                            lines.append(cut)
                            cut = ch
                    current = cut

        if current:
            lines.append(current)

        return lines

    def calc_block_height(self, paragraphs, max_width, has_title=False):
        lines = 0
        if has_title:
            lines += 1

        for p in paragraphs:
            wrapped = self.wrap_words(p, max_width)
            lines += len(wrapped) + 1

        return 16 + lines * self.line_height + 8

    def draw_paragraphs(self, surface, paragraphs, x, y, max_width, color):
        for p in paragraphs:
            lines = self.wrap_words(p, max_width)
            for line in lines:
                surface.blit(
                    self.font.render(line, True, color),
                    (x, y)
                )
                y += self.line_height
            y += 6
        return y
