with open("app/templates/base_tabler.html", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'class="theme-icon-dark d-flex align-items-center"' in line:
        line = line.replace('class="theme-icon-dark d-flex align-items-center"', 'class="theme-icon-dark d-none d-flex align-items-center"')
        new_lines.append(line)
    elif 'class="theme-icon-light d-flex align-items-center"' in line:
        line = line.replace('class="theme-icon-light d-flex align-items-center"', 'class="theme-icon-light d-none d-flex align-items-center"')
        new_lines.append(line)
    else:
        new_lines.append(line)

with open("app/templates/base_tabler.html", "w") as f:
    f.writelines(new_lines)
