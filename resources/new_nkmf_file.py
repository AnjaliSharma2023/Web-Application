# New NKMF File
# 
# https://github.com/bizzlebin/team_6/blob/master/resources/new_nkmf_file.py
# 
# new_nkmf_file.py
# 
# ***
# 
# By JBT
# 
# ***
# 
# Created 2021-01-19
# 
# ***
# 
# Copyright © JBT
# 
# All rights reserved. ***Pre-release: do not distribute!***
# 
# """THE WORK IS PROVIDED "AS IS" AND THE AUTHORS AND OWNERS DISCLAIM ALL WARRANTIES WITH REGARD TO THIS WORK INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHORS OR OWNERS BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS WORK."""
# 
# +++
# Description
# 
# A small program to automatically create the basic NK Metadata Format header for all sorts of text files, from plaintext to code, and provide the full template for all code files; author is currently hard-coded and almost no error-checking is done as the point is to streamline most work while failing on [hopefully few] edge cases [which need user interventions and/or a code update].
# 

# 
# +++
# Imports
# 
from string import Template
import tkinter
from tkinter import filedialog
from datetime import datetime
from os import sys
# 
# +++
# Assignments
# 
# ===
# Initializations
# 
# ===
# Constants
# 
AUTHOR = 'JBT' # User-set identifier

EXTS = \
	(
	('Text file', '*.txt'),
	('C file', '*.c'),
	('C++ file', '*.cpp'),
	('JavaScript file', '*.js'),
	('Python file', '*.py'),
	('All files', '*.*'),
	)
DEFAULT_EXT = '.txt'
HEADER_TEMPLATE = Template('''$title

$uri

***

By $AUTHOR

***

Created $created

+++
Description

[add 6 Cs-compliant description]''')
CODE_TEMPLATE = '''
+++
Imports

[code]

+++
Assignments

===
Initializations

[code]

===
Constants

[code]

+++
Functions

===
Classes

[code]

===
Definitions

[code]

+++
Output

[code]'''
# 
# +++
# Functions
# 
# ===
# Classes
# 
# ===
# Definitions
# 
# ---
# Create Strict Snake Case
# 
def create_strict_snake_case(text):
	'''
	Convert an arbitrary string into UEWSG-compliant (and RFC 3986 §2.3-compliant) strict snake case.

	This function takes any string and, using the rules set for for filenames in the UEWSG (and based in turn upon RFC 3986 §2.3, which is nearly a subset of "POSIX-portable" as well, not counting the tilde ("~")), converts it into strict snake case by stripping leading and trailing whitespace, lowercasing all letters, replaing spaces with underscores, and then stripping out any remaining non-compliant characters.

	**text**: str (text to be converted)

	Return text: str (in UEWSG-compliant strict snake case)
	'''

	NUMBERS = {chr(48 + i) for i in range(10)} # 0–9
	LETTERS = {chr(97 + i) for i in range(26)} # Lowercase only
	OTHERS = {'-', '_', '.', '~'} # Also from RFC 3986 §2.3
	UNRESERVED_CHARACTERS = NUMBERS | LETTERS | OTHERS # From the UEWSG (RFC 3986 §2.3 minus uppercase letters, which aren't part of the UEWSG spec)

	text = text.strip() # Extra whitespace is only permitted in [preformatted] quotes
	text = text.casefold() # Only lowercase letters are permitted in strict snake case
	text = text.replace(' ', '_') # Spaces are replaced with underscores
	for character in text:
		if character not in UNRESERVED_CHARACTERS:
			text = text.replace(character, '') # All non-conforming characters are simply deleted

	return text
# 
# ---
# Create Comments
# 
def create_comments(text, comment_marker):
	'''
	Create UEWSG-compliant comments for arbitrary code.

	**text**: str (multiline strings fine)
	**comment_marker**: str (character *plus* space)

	Return comments: str (fully-commented text)
	'''

	comments = ''
	for line in text.splitlines(keepends = True): # Keep newline characters
		if line == '[code]\n':
			comments += '\n'
		elif line == '[code]': # Handle case where last line is "[code]"
			pass
		else:
			comments += f'{comment_marker}{line}'
	return comments
# 
# ---
# Read Comment Marker
# 
def read_comment_marker(ext):

	'''
	Read the most common types of file extensions in NK and return the associated single-line comment marker.

	**ext**: str (the file extension, *not* including the preceding period)

	Return comment_marker: str (single-line comment marker, *including* space)
	'''
	C_STYLE_COMMENT_EXTS = 'c', 'cpp', 'js'
	C_STYLE_COMMENT_MARKER = '// '

	SHELL_STYLE_COMMENT_EXTS = 'py',
	SHELL_STYLE_COMMENT_MARKER = '# '

	if ext in C_STYLE_COMMENT_EXTS:
		comment_marker = C_STYLE_COMMENT_MARKER
	elif ext in SHELL_STYLE_COMMENT_EXTS:
		comment_marker = SHELL_STYLE_COMMENT_MARKER
	else:
		comment_marker = ''

	return comment_marker
# 
# +++
# Output
# 
# ===
# Main
# 
def main():

	try:
		print('[New NKMF File header]')
		print()
		print('+++')
		print('Output')
		print()
		title = input('Enter the file\'s [Metadata Format] title and version: ').strip() # Does not test for compatibility but provides basic error correction in stripping leading and trailing whitespace, which is only permitted in [preformatted] quotes

		name = create_strict_snake_case(title)

		root = tkinter.Tk() # """root""" seems to be the most common default
		root.withdraw() # Hide/unmake the root window; from https://stackoverflow.com/questions/9319317/quick-and-easy-file-dialog-in-python
		uri = tkinter.filedialog.asksaveasfilename(title = 'File Name', initialfile = name, filetypes = EXTS, defaultextension = DEFAULT_EXT) # Using Tkinter is slower CPU-wise but faster human-wise because of the GUI and its natural error boundaries/checking/correction; """initialdir""" does not support "%USERPROFILE%" string and similar Windows conventions else it would be nice to use

		created = datetime.now().strftime('%Y-%m-%d') # ISO 8601-compliant date

		ext = uri.rsplit(sep = '.', maxsplit = 1)[1] # Handles only files with extensions, as per UEWSG, else this line will throw an exception

		header = HEADER_TEMPLATE.substitute(title = title, uri = uri, AUTHOR = AUTHOR, created = created)

		comment_marker = read_comment_marker(ext)

		with open(uri, 'w', encoding = 'UTF-8') as file:
			if comment_marker:
				file.write(create_comments(header, comment_marker))
				file.write(f'\n{comment_marker}\n\n') # End Description paragraph line, end [commented] division, and insert blank line to separate header from code, as per Code Format spec; one statement for increased I/O performance
				file.write(create_comments(CODE_TEMPLATE, comment_marker))
			else:
				file.write(header)
	except: # Catch all exceptions for basic pass/fail operation; this is a tool to make a task easier, not a full gatekeeper or mission-critical program, so failing hard and fast will likely be better UX than a long-winded explanation or decision tree that over-corrects for what likely is a simple mistake and just generally slows down the process
		print()
		input('**Error**: Could not create new file; please check your title, filename, extension, and folder permissions! Press Enter to exit...')
		sys.exit()
# 
# ===
# Init
# 
if __name__ == '__main__':
	main()
# 
# +++
# Todo
# 
# • Make Read NKCF Header
# • Make """create_strict_snake_case()""" a separate module
# • Test "*nix" support