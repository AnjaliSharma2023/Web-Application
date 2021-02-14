import os
import re

# The color can be denoted by: {% color_category color_choice %}
# The amount of whitespace is negligible except that the percent signs must be right next to the curly braces and there must be at least one between the category and choice
# text_color color1 should be text that is in front of background_color color1, etc.

# Color dict to be assigned from, keys are used in .template files
COLOR_DICT = {
    'background_color': {
        'color1': '#333', # Nav bar background color
        'color2': '#4CAF50', # Nav bar selected page color
        'hover1': '#ddd', # Nav bar hovered item color
        },
    'text_color': {
        'color1': '#f2f2f2', # Nav bar text color
        'color2': 'white', # Nav bar selected page text color
        'color3': 'black', # Content text color
        'hover1': 'black', # Nav bar hovered item text color
        }
}


# Get file locations in this directory
for root, dirs, files in os.walk(os.getcwd()):
    # Skip .py file directory
    if 'assignColors.py' in files:
        continue

    for file in files:
        # Skip files that are not .template
        if file.split('.')[-1] != 'template':
            continue
        
        # Open .template files
        with open(os.path.join(root, file), 'r') as template_file:
            # Create string to be written to the new file
            new_file = ''
            # Create pattern to match the spots to input colors
            pattern = re.compile(r".*\{%(\s*\w*)(\s+)(\w*\s*)%\}.*")
            # Iterate through lines
            for line in template_file.readlines():
                # Match all occurences in the line
                while pattern.match(line):
                    # Replace text with info from the color dict
                    match = pattern.match(line)
                    line = line.replace(f'{{%{match[1]}{match[2]}{match[3]}%}}', COLOR_DICT[match[1].strip()][match[3].strip()])
                
                # Add new or unchanged line
                new_file += line
                
        # Create the new file and write the prepared string
        with open(os.path.join(root, '.'.join(file.split('.')[:-1])), 'w') as gen_file:
            gen_file.write(new_file)