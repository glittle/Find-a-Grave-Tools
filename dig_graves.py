# --------------------------------------------
# Author: D. Foster
# Author URI: http://convinsys.com
# Copyright: 2024 Convinsys, All rights reserved
# Last update: 2024/05/26 @ 01:15pm
# Comments: Dig "Find a Grave" cemeteries for totals.
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

cemetery = ['1234']
surname = ['foster']
name = ['doug', 'bill', 'jerome']
nickname = ['me']
id = ['23']
birth = ['1956-05-28']
death = ['TBD']
parents_surname = ['something']
parents = ['Sadie']
spouses = ['Cindy']
father = ['Lowell']
mother = ['Sadie']
veteran = [False]
cenotaph = ['dd']
plot = ['h1']
bio = ['bio sdfkjh sdf']
google_map = ['https://dfsdf.com']
latitude = ['2344']
longitude = ['-22294.4']
inscription = ['watch me']
gravesite_details = ['details']
notes = ['ta da']
burial_type = ['normal']

header = {
	'A' : 'Cemetery',
	'B' : 'Surname',
	'C' : 'Name',
	'D' : 'Nickname',
	'E' : 'ID',
	'F' : 'Birth',
	'G' : 'Death',
	'H' : 'Parent\'s Surname',
	'I' : 'Parents',
	'J' : 'Spouses',
	'K' : 'Father',
	'L' : 'Mother',
	'M' : 'Veteran',
	'N' : 'Cenotaph',
	'O' : 'Plot',
	'P' : 'Bio',
	'Q' : 'Google Map',
	'R' : 'Latitude',
	'S' : 'Longitude',
	'T' : 'Inscription',
	'U' : 'Gravesite Details',
	'V' : 'Notes',
	'W' : 'Burial Type',
}
data = {
	'A' : cemetery,
	'B' : surname,
	'C' : name,
	'D' : nickname,
	'E' : id,
	'F' : birth,
	'G' : death,
	'H' : parents_surname,
	'I' : parents,
	'J' : spouses,
	'K' : father,
	'L' : mother,
	'M' : veteran,
	'N' : cenotaph,
	'O' : plot,
	'P' : bio,
	'Q' : google_map,
	'R' : latitude,
	'S' : longitude,
	'T' : inscription,
	'U' : gravesite_details,
	'V' : notes,
	'W' : burial_type,
}

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('trial1.xlsx')
worksheet = workbook.add_worksheet()

# Add a bold format to use to highlight cells.
bold = workbook.add_format({'bold': 1})

# --- Write headers. ---
for key, item in header.items() : # Loop
	worksheet.write(key + str(1), item, bold)

# Loop, increment row.
row = 2 # row = 3,4, ... for all master records
for key, item in data.items() : # Loop
	worksheet.write(key + str(row), item[row-2], bold)

workbook.close()

# cols['Parents'][2] = "white"

# --- Functions. ---

# --- Test. ---

# --- Get digging instructions. ---
# instructions = grave_digger.dig_instructions()

# --- Start. ---
# toolbox.print_l('Started script @ ' + time.strftime('%Y%m%d-%H%M%S') + '.')

# --- Loop cemeteries. ---
# total_pages=0
# for cemetery_id, groups in instructions.items() :
# 	cemetery_folder = glob.glob(path_to_start + cemetery_id + '_*')[0]
# 	group_folders = glob.glob(cemetery_folder + '/' + cemetery_id + '**/' )

# 	# --- Loop group folders.
# 	for group_folder in group_folders :

# 		# --- Page counts. ---
# 		num = len(os.listdir(group_folder))
# 		total_pages += num
# 		page_counts.update({group_folder: num})


