# ------------------------------------------------\
#  Generalized functions for find-a-grave-tools.
#  Last update: 2024/06/04 @ 03:00pm.
#
#  Name:               toolbox.py
#  URI:                https://github.com/doug-foster/find-a-grave-tools
#  Description:	       Generalized functions for find-a-grave-tools
#  Version:            1.2.0
#  Requires at least:  3.1 Python
#  Prefers:            3.12 Python
#  Author:             Doug Foster
#  Author URI:         http://dougfoster.me
#  License:            GPL v3 or later
#  License URI:        https://www.gnu.org/licenses/agpl-3.0.html
#  Update URI:         https://github.com/doug-foster/find-a-grave-tools
#  Text Domain:        find-a-grave-tools
# ------------------------------------------------\

# --- Import libraries. ---
# Standard Libraries.
import time  # https://docs.python.org/3/library/time.html
import os  # https://docs.python.org/3/library/os.html
import random  # https://docs.python.org/3/library/random.html
import re  # https://docs.python.org/3/library/re.html
import inspect  # https://docs.python.org/3/library/inspect.html
import html  # https://docs.python.org/3/library/html.html
# Packages.
# My modules.

# --- Globals. ---
path_to_instructions = 'instructions/'
log_file = None

# --- Functions. ---
# pause(low, high, status)
# get_instructions(level)
# remove_last_byte(f, path)
# print_l(string, end)
# log(start)
# get_url(session, url)

# --------------------------------------------\
#  Pause a random amount of time.
#  Last update: 2024/05/28 @ 01:45pm.
#
#  Low & high are seconds.
#  Helpful for rate pacing.
# --------------------------------------------\
def pause(low:float = 0, high:float = 2.0, status:bool = False) :

	# --- Check input. ---
	if low > high :
		print_l('Error: min(' + str(low) + ') > max(' + str(high) + ')')
		return False
	
	# --- Vars. ---
	min = int(low)*100
	max = int(high)*100

	# --- Calculate pause time. ---
	pause_time = round(random.randint(min,max)/100, 2)
	if status :
		print_l('  Pause for ' + str(pause_time) + ' seconds')

	# -- Pause. --
	time.sleep(pause_time)
	return True
# --------------------------------------------/


# --------------------------------------------\
#  Read data from an instructions file, return as a list.
#  Last update: 2024/05/28 @ 10:30am.
#
#  Naming format - /instructions/script.txt for script.py.
# --------------------------------------------\
def get_instructions(level:int = 0) :

	# --- Vars. ---
	level += 1
	called_by = inspect.stack()[level].filename
	file_name_parts = called_by.rsplit('\\',1)
	file_path = file_name_parts[0] + '\\' + path_to_instructions
	file_stub = file_name_parts[1]
	file_short_name = file_stub.replace('.py', '.txt')
	file_full_name = file_path + file_short_name
	skip_line_starts = ['#', '', ' ', '\n']
	instructions = []

	# --- Check input. ---
	if not os.path.exists(file_full_name) : # Does file exist?
		print_l('Error: "' + file_short_name + '" does not exist.')
		return False

	# --- Read file. ---
	f = open(file_full_name, 'r')
	lines = f.readlines()
	f.close

	# --- Return an array of data to use. ---
	for line in lines :
		if line[0] in skip_line_starts :
			continue # Skip line.
		instructions.append(line)
	
	return instructions
# --------------------------------------------/


# --------------------------------------------\
#  Remove the last byte from a file.
#  Last update: 2024/05/28 @ 10:30am.
#
#  Usually it's a dangling "\n" from writing lines.
# --------------------------------------------\
def remove_last_byte(f, path) :

	# --- Read/write file. ---
	if os.path.getsize(path) > 0 :
		f = open(path, 'br+')
		f.truncate(f.seek(-1, 2))
		f.close()
# --------------------------------------------/


# --------------------------------------------\
#  Replace print with print & log.
#  Last update: 2024/06/01 @ 06:15pm.
# --------------------------------------------\
def print_l(string:str = '', last:str = '\n') :

	# --- Print/log file. ---
	print(string, end=last)
	if None != log_file :
		log_file.write(string + '\n')
# --------------------------------------------/

# --------------------------------------------\
#  Open & close a log file.
#  Last update: 2024/05/28 @ 10:30am.
# --------------------------------------------\
def log(start:bool = True) :

	# --- Vars. ---
	global log_file

	# --- Open/close file. ---
	if start :
		name = 'logs/' + time.strftime('%Y%m%d-%H%M%S') + '_output.txt'
		log_file = open(name, 'w')
		return name
	else :
		if None != log_file :
			log_file.close()
# --------------------------------------------/


# --------------------------------------------\
#  Given an open session, request a URL.
#  Last update: 2024/05/28 @ 10:30am.
# --------------------------------------------\
def get_url(session, url) :

	# --- Vars. ---
	tries = 3

	# --- Request URL. ---
	while tries > 0 :  # Multiple request tries needed?
		request = session.get(url)
		if request.status_code == 200 :  # Request worked.
			return request
		else :
			print_l('Error: ' + url)
			tries -= 1
			if 0 == tries :
				print_l('No retries remain. Giving up. Early exit.')
				quit()
			else :
				print_l(str(tries) + ' retries remaining. Trying again. ')
				pause(3, 5, True)  # Pause.
	
	return False
# --------------------------------------------/


# --------------------------------------------\
#  Improve the readability of a string.
#  Last update: 2024/06/10 @ 02:45pm.
# --------------------------------------------\
def clean_string(string) :

	# --- Vars. ---
	before = string

	# --- Repair. ---
	string = string.replace('<br>', '</br>')
	string = string.replace('</br>', '<br/>')

	# --- Replace. ---
	string = html.unescape(string)  # Html characters (&amp; etc.).
	string = string.replace('<I>', '')  # 'italics' tags.
	string = string.replace('</I>', '')  # 'italics' tags.
	string = string.replace('<I>', '')  # 'bold' tags.
	string = string.replace('</I>', '')  # 'bold' tags.
	string = string.replace('<strong>', '')  # 'strong' tags.
	string = string.replace('</strong>', '')  # 'strong' tags.
	string = re.sub('(<div)(.*?)(>)', '', string)  # Opening 'div' tags.
	string = string.replace('</div>', '\n')  # Closing 'div' tags.
	string = re.sub('(<p)(.*?)(>)', '', string)  # Opening 'p' tags.
	string = string.replace('</p>', '\n')  # Closing 'p' tags.
	string = string.replace('<br/>', '\n')  # Line breaks.
	string = string.lstrip().lstrip('\n')  # Beginning of string.
	string = string.rstrip().rstrip('\n')  # End of string.
	string = string.replace('\n\n\n', '\n\n')  # Multiple newlines.
	string = string.replace('   ', ' ')  # Multiple (3) spaces.
	string = string.replace('  ', ' ')  # Multiple (2) spaces.
	return string
# --------------------------------------------/

# ------------------------------------------------/
