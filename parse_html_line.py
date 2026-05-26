from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.div_depth = 0
        self.tab_content_depth = -1
        self.history_depth = -1

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.div_depth += 1

    def handle_endtag(self, tag):
        if tag == 'div':
            self.div_depth -= 1

parser = MyHTMLParser()
with open("app/templates/bodyweight.html", "r") as f:
    text = f.read()

lines = text.split('\n')
for i, line in enumerate(lines):
    parser.feed(line + '\n')
    if i + 1 == 397:
        print(f"At line 397, div_depth is {parser.div_depth}")
    if i + 1 == 399:
        print(f"At line 399, div_depth is {parser.div_depth}")
