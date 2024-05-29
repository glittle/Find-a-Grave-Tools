# --------------------------------------------
# Name:              dig_graves.py
# URI:               https://github.com/doug-foster/find-a-grave-scraper
# Description:	     Extract, analyze, and report data for https://www.findagrave.com memorial pages.
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
# Last update: # Last update: 2024/05/29 @ 01:15pm.
# Comments: 
# --------------------------------------------

# --- Import libraries. ---
# Standard Libraries
import time
import os
import glob
# Packages
from bs4 import BeautifulSoup
import xlsxwriter
# My modules
import toolbox
import grave_digger

# --- Functions. ---

# --- Globals. ---
path_to_stash = 'stash/'
path_to_output = 'output/'

# --- Get digging instructions. ---
instructions = grave_digger.dig_instructions()

# --- Start. ---
toolbox.print_l('Started script @ ' + time.strftime('%Y%m%d-%H%M%S') + '.')

# --- Create workbook. ---
workbook = xlsxwriter.Workbook(path_to_output + 'burials.xlsx')  # Create workbook.
worksheet = workbook.add_worksheet()  # Add aworksheet.

# --- Create cell formats. ---
bold = workbook.add_format({'bold': 1}) # Highlight bold.

# --- Digging instructions. ---
cemetery_ids = []
cemetery_groups = []
cemetery_folders = []
burial_folders = []
burial_lists = []
burials = []
fag_prefix = 'https://www.findagrave.com/memorial/'
lines = []

for cemetery_id, groups in instructions.items() : # Loop cemeteries.
	cemetery_ids.append(cemetery_id)
	cemetery_groups += groups
	cemetery_folder = glob.glob(path_to_stash + '/' + cemetery_id + '*_*/')[0]
	# Does cemetery folder exit?
	if not os.path.exists(cemetery_folder) :
		toolbox.print_l('Error: Folder for cemetery id="' + cemetery_id +
			'" does not exist.')
		quit()
	cemetery_folders.append(cemetery_folder)
	burial_folder = cemetery_folder + cemetery_id + '_burials'
	# Does burials folder exit?
	if not os.path.exists(burial_folder) :
		toolbox.print_l('Error: Burial folder for cemetery id="' + 
			cemetery_id + '" does not exist.')
		quit()
	burial_folders.append(burial_folder)
	burial_list = burial_folder + '_list.txt'
	# Does burials list file exit?
	if not os.path.exists(burial_list) :
		toolbox.print_l('Error: Burial list for cemetery id="' + 
			cemetery_id + '" does not exist.')
		quit()
	# Read burials from burial list file.
	f = open(burial_list, 'r')
	lines += f.read().splitlines()
	f.close
	# Set file path for each burial file.
	for line in lines :
		line = '_'.join(line.rsplit('/',1))
		line = burial_folder + '/' + line.replace(fag_prefix, '') + '.html'
		burials.append(line)

# Do the magic. Loop all columns for each row. Write one cell at a time.
# worksheet.write(row_num, col_num, data, *args)
num_row = 0
num_col = 0
# Write header.
cols_to_write = grave_digger.dig('', num_row)
for cell in cols_to_write :  # Loop columns.
	worksheet.write(num_row, num_col, cell, bold)  # Write header.
	num_col += 1
num_row = 1
# Write data.
for burial_file_name in burials :
	num_col = 0
	cols_to_write = grave_digger.dig(burial_file_name, num_row)  # Array of elements to write
	for cell in cols_to_write :  # Loop columns.
		worksheet.write(num_row, num_col, cell)  # Write data.
		num_col += 1
	num_row += 1
	if 2 == num_row :
		break

# --- Close & quit. ---
workbook.close()

# --- Test. ---
