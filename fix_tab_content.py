with open("app/templates/bodyweight.html", "r") as f:
    text = f.read()

# Check the number of `div` tags.
print("Div start tags:", text.count('<div'))
print("Div end tags:", text.count('</div'))
