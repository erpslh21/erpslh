with open("app/templates/bodyweight.html", "r") as f:
    text = f.read()

def count_tags(text, start, end):
    return text.count(start) - text.count(end)

print(count_tags(text, "<div", "</div"))
