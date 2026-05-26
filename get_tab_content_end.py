import re

with open("app/templates/bodyweight.html", "r") as f:
    text = f.read()

# Let's find the `tab-content` div and find where it ends.
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'class="tab-content"' in line:
        print(f"tab-content starts at line {i+1}")

    if '<!-- Admin Excel Export Tab -->' in line:
        print(f"Admin Excel Tab starts at line {i+1}")
