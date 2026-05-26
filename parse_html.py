from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.div_depth = 0
        self.tab_content_depth = -1
        self.history_depth = -1
        self.in_tab_content = False

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.div_depth += 1
            attr_dict = dict(attrs)
            if attr_dict.get('class') == 'tab-content':
                self.tab_content_depth = self.div_depth
                print(f"tab-content started at depth {self.div_depth}")
            if attr_dict.get('id') == 'tab-history':
                self.history_depth = self.div_depth
                print(f"tab-history started at depth {self.div_depth}")
            if attr_dict.get('id') == 'tab-excel-export':
                print(f"tab-excel-export started at depth {self.div_depth}. tab_content_depth={self.tab_content_depth}")

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.div_depth == self.tab_content_depth:
                print(f"tab-content ended at depth {self.div_depth}")
                self.tab_content_depth = -1
            if self.div_depth == self.history_depth:
                print(f"tab-history ended at depth {self.div_depth}")
                self.history_depth = -1
            self.div_depth -= 1

parser = MyHTMLParser()
with open("app/templates/bodyweight.html", "r") as f:
    parser.feed(f.read())
