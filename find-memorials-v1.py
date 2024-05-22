# --------------------------------------------
# Author: D. Foster
# Author URI: http://convinsys.com
# Copyright: 2024 Convinsys, All rights reserved
# Last update: 2024/05/22 @ 10:45am
# Comments:
# 1. Create a file of memorial URLs for a "Find a Grave" cemetery.
# --------------------------------------------

# --- Import libraries. ---
import requests
import time
import random
from bs4 import BeautifulSoup

# --- Globals. ---
max_pages = 200

# --- Functions. ---
def log_memorial() :
	# Write memorial URLs for each page to a file.
	# URL format: "https://www.findagrave.com/memorial/84600372/albert-mike-albrecht"
	memorials = soup.find_all('div', {'class' : 'memorial-item'}) # Search page for memorial items.
	for memorial in memorials : # Loop memorial items
		if len(memorial.find_all('a')) > 0 : # Check if item has a link.
			f.write('https://www.findagrave.com/' + memorial.a['href'] + '\n') # Record memorial.

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
soup = BeautifulSoup(request.content, 'html.parser')
cemetery_name = soup.find('h1', {'class' : 'bio-name'}).text.rstrip().lstrip().lower().replace(' ', '-')

# --- Create file for memorial URLs. ---
memorials_file = cemetery_name + '_' + cemetery + '_memorials_' + time.strftime('%Y%m%d-%H%M%S') + '.txt'
f = open(memorials_file, 'w')

# --- Loop cemetery memorial pages. ---
page = 1
loop = True
while (loop) :
	if (page == max_pages) :  # Prevent runaways.
		quit()
	cemetery_url_page = cemetery_url + '/memorial-search?page=' + str(page)  # Set page URL.
	request = session.get(cemetery_url_page)  # Get page.
	soup = BeautifulSoup(request.content, 'html.parser')
	warnings = soup.find_all('span', {'class' : 'icon-warning'}) # Search page tags for warnings.
	for warning in warnings :  # Loop warnings.
		if warning.parent.text.lower().find('no matches found') > 0 :  # No more pages warning.
			loop = False  # No more pages.
			break
	if (loop) :
		print('Pulling memorials from ' + cemetery_url_page)
		log_memorial()  # Process page.
	else :
		print('No more pages.')	
	page += 1  # Increment
	pause()

# --- Tweak & close memorials file. ---	
f.close()
f = open(memorials_file, 'br+')
f.truncate(f.seek(-1, 2)) # Got to file end, remove empty last line (byte = \n).
f.close()
print('Done.')	