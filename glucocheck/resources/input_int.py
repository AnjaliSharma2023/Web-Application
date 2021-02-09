# Input Int 3.0.0
# 
# https://github.com/bizzlebin/team_6/blob/master/resources/input_int.py
# 
# nkfs:/red/fire/tools/nkpy/input_int.py
# 
# ***
# 
# By JBT
# 
# ***
# 
# Created 2021-01-19
# 
# +++
# Description
# 
# A small module to simplify the process of obtaining a valid integer from the user; with basic error checking/handling.
# 
# Verifying user input is incredibly common in programs, so this is a function I have used, in one form or another, since CSC 121 in 2H 2019; this particular, streamlined implementation—with parameters to make it more customizable—traces back to CSC 256 .
# 

# 
# +++
# Imports
# 
from typing import Optional
# 
# +++
# Functions
# 
# ===
# Definitions
# 
# ---
# Input Int
# 
def input_int \
	(
	PROMPT: str,
	MIN: float = float('-inf'),
	MAX: float = float('inf'),
	ERROR: str = 'That is not a valid number!',
	ESCAPE: str = None
	) -> Optional[int]:
	'''
	Get a valid integer from the user.

	This function repeatedly asks the user for an integer using an arbitrary prompt, passed as an argument, until the input is valid or matches the escape string. The minimum and maximum valid numbers, inclusive, are fully tunable. All non-integers raise exceptions, as do invalid numbers; the function and error-handling are completely self-contained and the error message can be customized.
	'''

	while True:
		STRING: str = input(PROMPT)
		if STRING == ESCAPE:
			return None
		try:
			NUMBER: int = int(STRING)
			if NUMBER < MIN:
				raise ValueError
			if NUMBER > MAX:
				raise ValueError
			return NUMBER
		except ValueError:
			print(ERROR)
# 
# +++
# Output
# 
if __name__ == '__main__':
	while True:
		print(input_int('"""input_int()""" driver: '))
# 
# +++
# Changelog
# 
# **3.0.0**: (2020-12-17) Updated parameters to identify constants.
# **2.2.0**: (2020-11-12) Added driver for quick testing.
# **2.1.0**: (2020-11-11) Added type annotations so the docstring follows the new format: no more redundant parameter and return documentation! Further, the parameters now follow the Whitesmiths style, as per the [NK]CF (version 2020-10-17), for easier readability.
# **2.0.0**: (2020-09-16) Renamed to input_int.py (as per [NK] Code Format CURD-based naming conventions), changed return to """None""" on escape for more consistent return handling.
# **1.0.0**: (2020-08-19) Derived from get_float.py, which was originally created for CSC 256 earlier the same day.