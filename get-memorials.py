# --------------------------------------------
# Author: D. Foster
# Author URI: http://convinsys.com
# Copyright: 2024 Convinsys, All rights reserved
# Last update: 2024/05/22 @ 02:30pm
# Comments:
# 1. Create a cache directory of pages for a "Find a Grave" cemetery.
# --------------------------------------------

# --- Import libraries. ---
# Standard Libraries
import time
import random
import os
import shutil
# Packages
import requests
from bs4 import BeautifulSoup

# --- Globals. ---
max_pages = 200
data_folder = 'data/'
date_time = time.strftime('%Y%m%d-%H%M%S')
memorial_urls = []

# --- Functions. ---
def pause() :
	# Random pause between website page requests; don't look like a DOS attack.
	min = 50
	max = 120
	pause_time = round(random.randint(min,max)*0.01, 2)
	print('Pause for ' + str(pause_time) + ' seconds')
	time.sleep(pause_time)

def do_page() :
	# --- Write memorial URLs for this page to the file. ---
	global memorial_urls, loop  # Global values to be modified.
	soup = BeautifulSoup(request.content, 'html.parser')
	warnings = soup.find_all('span', {'class' : 'icon-warning'}) # Search page tags for warnings.
	for warning in warnings :  # Loop warnings.
		if warning.parent.text.lower().find('no matches found') > 0 :  # No more pages warning.
			loop = False # No more pages.
			print('No more pages.')
			return False
	print('Pulling memorials from ' + cemetery_url_page)
	# URL format: "https://www.findagrave.com/memorial/84600372/albert-mike-albrecht"
	memorials = soup.find_all('div', {'class' : 'memorial-item'}) # Search page for memorial items.
	for memorial in memorials : # Loop memorial items
		if len(memorial.find_all('a')) > 0 : # Check if item has a link.
			memorial_url = 'https://www.findagrave.com/' + memorial.a['href']
			f.write(memorial_url + '\n') # Record memorial.
			memorial_urls.append(memorial_url)

# --- Get cemetery id. ---
cemetery_id = input('Enter cemetery id: ')
cemetery_url = 'https://www.findagrave.com/cemetery/' + cemetery_id

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

# --- Create cemetery folder. ---
soup = BeautifulSoup(request.text, 'html.parser')
cemetery_name = soup.find('h1', {'class' : 'bio-name'}).text.rstrip().lstrip().lower().replace(' ', '-')
cemetery_folder = data_folder + cemetery_id + '_' + cemetery_name
if os.path.exists(cemetery_folder) :  # Does folder exist?
	shutil.rmtree(cemetery_folder)  # Delete folder & files, start over.
	time.sleep(1)
os.mkdir(cemetery_folder)  # Create a new folder.
time.sleep(1)

# --- Save cemetery html page. ---
cemetery_label = cemetery_folder + '/cemetery_' + cemetery_id + '_'
cemetery_page = cemetery_label + 'page.html'
f = open(cemetery_page, 'w')
f.write(request.text)
f.close()

# --- Create memorial list file. ---
cemetery_list = cemetery_label + 'list.txt'
f = open(cemetery_list, 'w')

# --- Loop memorial pages. ---
page = 1
loop = True
while (loop) :
	if (page == max_pages) :  # Prevent runaways.
		quit()
	cemetery_url_page = cemetery_url + '/memorial-search?page=' + str(page)  # Set page URL.
	request = session.get(cemetery_url_page)  # Get page.
	if request.status_code != 200 :
		print('Cemetery url is not valid: ' + cemetery_url_page)
		quit()
	do_page()  # Each page has multiple links to memorials.
	if (loop) :
		page += 1  # Increment page.
		pause()  # Pace requests.

# --- Tweak & close memorial list file. ---	
f.close()
f = open(cemetery_list, 'br+')
f.truncate(f.seek(-1, 2)) # Got to file end, remove empty last line (byte = \n).
f.close()

# --- Loop memorial URLs. ---
num_memorials = len(memorial_urls)
this_memorial = 1
print('Processing ' + str(len(memorial_urls)) + ' memorials ...')
for memorial_url in memorial_urls :  # Loop URLs.
	print(str(this_memorial) + ' of ' + str(num_memorials) + ' - ' + memorial_url)
	request = session.get(memorial_url)  # Get memorial page.
	# https://www.findagrave.com/memorial/6906531/charles-edward-macfaden
	memorial_id = memorial_url.split('memorial/')[1].replace('/', '_')
	memorial_label = cemetery_folder + '/memorial_' + memorial_id + '_'
	memorial_page = memorial_label + '.html'
	f = open(memorial_page, 'w')
	f.write(request.text)  # Save memorial page.
	f.close()
	this_memorial +=1
	pause()  # Pace the requests.

# --- Done. ---
print('Done.')
