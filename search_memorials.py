# ------------------------------------------------\
#  Create a local stash of "Find a Grave" memorial pages.
#  Last update: 2024/06/10 @ 03:15pm.
#
#  Name:               stash_graves.py
#  URI:                https://github.com/doug-foster/find-a-grave-tools
#  Description:	       Create a local stash of "Find a Grave" memorial pages
#  Version:            1.2.2
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
# Standard Libraries
import time  #https://docs.python.org/3/library/time.html
import re
# Packages
import requests  # https://pypi.org/project/requests/
from bs4 import BeautifulSoup  # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# My modules
import toolbox  # https://github.com/doug-foster/find-a-grave-tools
import grave_digger  # https://github.com/doug-foster/find-a-grave-tools
import pandas as pd

# --- Globals. ---
cookie_domain = grave_digger.cookie_domain
path_to_stash = grave_digger.path_to_stash
burial_urls = []
master_list_of_urls = []
this_script = __file__.split('\\')
this_script = this_script[len(this_script)-1]

# --- Functions. ---

# --------------------------------------------\
# Search for memorials on a page.
# --------------------------------------------\
def get_memorials(session, searchInfo) :
    # split the searchInfo into the searchUrl and name based on ;
	searchUrl, searchType = searchInfo.split(';')
 
	plotNameToRemove = 'Last Supper'

	max_pages = 500
	page = 1
	loop = True
	memorialInfo = []
 
	# Define regex pattern for a date in the format of '31 Jan 1977' or 'unknown'
	date_pattern =  r'(?:\d{1,2} \w{3} )?(\d{4}|unknown)'

	while (loop) :

		# --- Prevent runaways. ---
		if (page == max_pages) :  # 
			toolbox.print_l('Error: exceeded max (' + max_pages + ') pages.')
			quit()

		# --- Get index page. ---
		url = searchUrl + '&page=' + str(page)
		toolbox.print_l('Loading ' + url)
		request = toolbox.get_url(session, url)

		# -- Make burial soup. --
		soup = BeautifulSoup(request.content, 'html.parser')

		# --- If last page, stop looping. ---
		# Search page tags for warnings.
		warnings = grave_digger.soup_find(soup, 'warnings')
		for warning in warnings :  # Loop warnings.
			# No more pages?
			if warning.parent.text.lower().find('no matches found') > 0 :
				loop = False # No more pages.
				break
		if not loop :
			break
	
		# Search page for memorial items.
		memorials = grave_digger.soup_find(soup, 'memorials')

		toolbox.print_l(searchType + ' - page ' + str(page) + ' has ' + str(len(memorials)) + ' memorials.')

		# --- Loop memorials ---
		for memorial in memorials : # Loop memorial items.
			memorial_url = memorial.a['href']
   
			# get the name after the last / in the url
			memorial_name = memorial_url.split('/')[-1]
   
   			# get last name from memorial name a-b-c -> c  and get first names a-b-c -> a-b
			memorial_name = memorial_name.split('-')[-1] + ', ' + '-'.join(memorial_name.split('-')[:-1])
   
			# capitalize each word in the name and replace _ with a space
			memorial_name = memorial_name.replace('_', ' ').replace('-', ' ').title()
   
			small_tag = memorial.find('small')  # Find the first <small> tag in the current 'div'
			needsPhoto = small_tag and 'No grave photo' in small_tag.get_text(strip=True)

			h2 = memorial.find('i', {'class' : 'pe-2'})
			name = h2.get_text(strip=True) if h2 else None

			# get plot, and strip out "Last Supper"
			strong = memorial.strong
			plot = re.sub(plotNameToRemove, '', strong.get_text(strip=True), flags=re.IGNORECASE) if strong else None
   
			b = memorial.find('b', {'class' : 'birthDeathDates'})
			dates = b.get_text(strip=True) if b else None

			# dates may have:
			#   unknown – 31 Jan 1977
			#   31 Jan 1977 - unknown
			#   Birth and death dates unknown.
			#	unknown – 1993
   			#   31 Jan 1927 - 31 Jan 1977
			# extract the birth and death dates
			birthAndDeath = ''
			if dates == 'Birth and death dates unknown.':  # If both dates are unknown, assign them as such
				birthAndDeath = 'unknown'
			else:
				matches = re.findall(date_pattern, dates.lower())
				# Depending on the number of matches, assign them to birth and death
				if len(matches) == 2:
					birthAndDeath = matches[0] + '-' + matches[1]  # Two dates found: assign them
					birthAndDeath = birthAndDeath.replace('unknown', '?')
				else:
					birthAndDeath = matches[0]  # Only one date found: assign it

			# if there is a photo, retrieve the page and look for "Photo added by <a href=...>NAME</a>" and get the name
			photographer = None
			# only do this if the searchTitle includes "HasGps"
			if not needsPhoto and searchType.find('Has GPS') > 0:
				photo_request = toolbox.get_url(session, 'https://www.findagrave.com' + memorial_url)
				photo_soup = BeautifulSoup(photo_request.content, 'html.parser')
				photo_tag = photo_soup.find('figure', {'id' : 'profile-photo'})
				if photo_tag:
					photographer = photo_tag.p.a.get_text(strip=True)

			# if photographer is Priscilla, set instructions to "Update GPS"; if needsPhoto, say "Take Photo" otherwise say "-"
			instructions = 'Update GPS' if photographer == 'Priscilla' else 'Take Photo' if needsPhoto else 'Add GPS' if searchType.find('No GPS') > 0 else '-'

			memorialInfo.append({
			'memorial-name': memorial_name, 
			'dates': birthAndDeath,
            'plot': plot,
			'instructions': instructions,
			'#': memorial_url.split('/')[2],
			'searchType': searchType,
			'full-name': name, 
			'raw-dates': dates,
			'noPhoto': needsPhoto,
			'photographer': photographer,
			'url': memorial_url, 
			})
   
			toolbox.print_l('       ' + memorial_name)
			

		if (loop) :
			#break
			page += 1  # Increment page.
			toolbox.pause(0.5,2,True)  # Pace requests.

	return memorialInfo

# --------------------------------------------/	



# --- Get digging instructions. ---
searchInfos = grave_digger.getUrls()

# --- Start. ---
toolbox.print_l('Started script @ ' + time.strftime('%Y%m%d-%H%M%S') + '.')

# --- Establish a new "browser" session. ---
# https://stackoverflow.com/questions/73688432/python-request-with-cookies-content-blocked-by-cookie-banner
session = requests.Session()
descriptor = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,'
descriptor += ' like Gecko) Chrome/104.0.5112.79 Safari/537.36'
headers = {
	'User-Agent': descriptor
}
session.headers.update(headers)
session.cookies.set("name", "notice_preferences", domain=cookie_domain)
session.cookies.set( "value", "2:", domain=cookie_domain)

memorials = []

# --- Digging instructions. ---
for searchInfo in searchInfos : # Loop cemeteries.
	memorials.extend(get_memorials(session, searchInfo))
 
	
# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(memorials)

# Save the DataFrame to an Excel file
stop_time = time.strftime('%Y%m%d-%H%M%S')

df.to_excel('memorial_data_' + stop_time + '.xlsx', index=False)

print("Data saved to memorial_data.xlsx")



# --- Wrap up. ---
toolbox.print_l()  # User status - readability.
toolbox.print_l('Finished script @ ' + stop_time + '.')
toolbox.print_l('Done.')

# ------------------------------------------------\
