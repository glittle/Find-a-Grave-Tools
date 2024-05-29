# --------------------------------------------
# Name:              toolbox.py
# URI:               https://github.com/doug-foster/find-a-grave-scraper
# Description:	     Generalized functions for find-a-grave-scraper
# Version:		     1.00
# Requires at least: 3.1
# Requires Python:   3.12
# Author:            Doug Foster
# Author URI:        http://dougfoster.me
# License:           GPL v3 or later
# License URI:       https://www.gnu.org/licenses/agpl-3.0.html
# Update URI:        https://github.com/doug-foster/find-a-grave-scraper
# Text Domain:       find-a-grave-scraper
#
# Last update: 2024/05/28 @ 10:30pm.
# Comments: 
# --------------------------------------------

# --- Import libraries. ---
# Standard Libraries.
import time
import os
import random
import inspect
# Packages.
import inspect
# My modules.

# --- Globals. ---
path_to_instructions = 'instructions/'
log_file = None

# --- Functions. ---
def pause(low:float = 0, high:float = 2.0, status:bool = False) :
	# --------------------------------------------
	# Pause a random amount of time.
	# Low & high are seconds.
	# Helpful for rate pacing.
	# Last update: 2024/05/28 @ 01:45pm.
	# --------------------------------------------

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

def get_instructions(level:int = 0) :
	# --------------------------------------------
	# Read data from an instructions file, return as a list.
	# Naming format - /instructions/script.txt for script.py.
	# Last update: 2024/05/28 @ 10:30am.
	# --------------------------------------------

	# --- Vars. ---
	level += 1
	called_by = inspect.stack()[level].filename
	file_name_parts = called_by.rsplit('/',1)
	file_path = file_name_parts[0] + '/' + path_to_instructions
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

def remove_last_byte(f, path) :
	# --------------------------------------------
	# Remove the last byte from a file.
	# Usually it's a dangling "\n" from writing lines.
	# Last update: 2024/05/28 @ 10:30am.
	# --------------------------------------------

	# --- Read/write file. ---
	if os.path.getsize(path) > 0 :
		f = open(path, 'br+')
		f.truncate(f.seek(-1, 2))
		f.close()
	
def print_l(string:str = '', end:str = '\n') :
	# --------------------------------------------
	# Replace print with print & log.
	# Last update: 2024/05/28 @ 10:30am.
	# --------------------------------------------
	
	# --- Print/log file. ---
	print(string)
	if None != log_file :
		log_file.write(string + '\n')

def log(start:bool = True) :
	# --------------------------------------------
	# Open & close a log file.
	# Last update: 2024/05/28 @ 10:30am.
	# --------------------------------------------

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

def get_url(session, url) :
	# --------------------------------------------
	# Given an open session, request a URL.
	# Last update: 2024/05/28 @ 10:30am.
	# --------------------------------------------

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
