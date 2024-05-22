# --------------------------------------------
# Author: D. Foster
# Author URI: http://convinsys.com
# Copyright: 2024 Convinsys, All rights reserved
# Last update: 2024/05/21 @ 11:05pm
# Comments: 
# 1. Read a file of memorial URLs for a "Find a Grave" cemetery.
# 2. Create a file with GPS coordinates for each memorial.
# --------------------------------------------

# --- Import libraries. ---
import time
import random
import os
import glob

import requests
from bs4 import BeautifulSoup

# --- Globals. ---

# --- Functions. ---
def process_memorial() :
	id = memorial_url.split('/memorial/')[1].split('/')[0]
	name = soup.find(id='bio-name').text.rstrip()
	location = soup.find(id='gpsValue')
	gmap = location.attrs['href']
	if gmap.find('maps.google') > 0 : # Check for no GPS data.
		lat_long = location.attrs['href'].split('?')[1].split('&')[0].split('=')[1]
		lat=lat_long.split(',')[0]
		long=lat_long.split(',')[1]
	else :
		gmap = 'No GPS data'
		lat=''
		long=''
	# Record coordinate data.
	if this_memorial == 1 :
		f.write('Find a Grave URL;Memorial ID;Name;Google maps URL;Lat;Long\n' )
	f.write(memorial_url + ';' + id + ';' + name + ';' + gmap + ';' + lat + ';' + long + '\n' )
	print(str(this_memorial) + ' of ' + str(num_memorials) + ' - ' + memorial_url)

def pause() :
	# Random pause between website page requests; don't look like a DOS attack.
	min = 5
	max = 20
	pause_time = round(random.randint(min,max)*0.01, 2)
	print('Pause for ' + str(pause_time) + ' seconds')
	time.sleep(pause_time)

# --- Get cemetery id. ---
cemetery = input('Enter cemetery id: ')
if cemetery == '' :
	# Sherill UCC = 2243718
	cemetery = '2243718'
cemetery_url = 'https://www.findagrave.com/cemetery/' + cemetery

# --- Establish new session. ---
# https://stackoverflow.com/questions/73688432/python-request-with-cookies-content-blocked-by-cookie-banner
session = requests.Session()
headers = {
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'
}
session.headers.update(headers)
session.cookies.set("name", "notice_preferences", domain="www.findagrave.com/")
session.cookies.set( "value", "2:", domain="www.findagrave.com/")

# --- Check for valid cemetery. ---
request = session.get(cemetery_url)
if request.status_code != 200 :
	print('Cemetery url is not valid: ' + cemetery_url)
	quit()

# --- Check for valid file of memorial URLs. ---
memorial_file_pattern = '*_' + cemetery + '_memorials*.txt'
files = glob.glob(memorial_file_pattern)  # Find the memorial file(s).
if len(files) == 0 :
	print('Memorial file(s) not found: ' + memorial_file_pattern)
	quit()

# --- Read (newest) file of memorial URLs. ---
newest = 0
memorial_file = ''
for file in files :  # Multiple files, find the newest one.
	created = os.path.getctime(file)
	if created > newest :
		memorial_file = file
		newest = created

# --- Read all memorial URL lines in file. ---
# URL format: "https://www.findagrave.com/memorial/84600372/albert-mike-albrecht"
f_m = open(memorial_file, 'r')
memorial_urls = f_m.readlines()
f_m.close()
print('Pulling ' + str(len(memorial_urls)) + ' memorials from ' + memorial_file)

# --- Create file for memorial coordinates. ---
soup = BeautifulSoup(request.content, 'html.parser')
cemetery_name = soup.find('h1', {'class' : 'bio-name'}).text.rstrip().lstrip().lower().replace(' ', '-')
coordinates_file = cemetery_name + '_' + cemetery + '_memorials_' + time.strftime('%Y%m%d-%H%M%S') + '.csv'
f = open(coordinates_file, 'w')

# --- Loop cemetery memorial pages. ---
num_memorials = len(memorial_urls)
this_memorial = 1
for memorial_url in memorial_urls :  # Loop URLs.
	memorial_url = memorial_url.split('\n')[0]  # Strip newline.
	request = session.get(memorial_url)  # Get memorial page.
	soup = BeautifulSoup(request.content, 'html.parser')
	process_memorial()  # Process page.
	if this_memorial != num_memorials :
		this_memorial += 1
		pause()  # Pace the requests.

# --- Tweak & close memorials file. ---	
f.close()
f = open(coordinates_file, 'br+')
f.truncate(f.seek(-1, 2)) # Got to file end, remove empty last line (byte = \n).
f.close()
print('Done.')