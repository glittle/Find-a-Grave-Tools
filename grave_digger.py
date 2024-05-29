# --------------------------------------------
# Name:              grave_digger.py
# URI:               https://github.com/doug-foster/find-a-grave-scraper
# Description:	     Specific functions for find-a-grave-scraper
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
# Last update: 2024/05/29 @ 01:15pm.
# Comments: 
# --------------------------------------------

# --- Import libraries. ---
# Standard Libraries.
import os
import glob
import re
# Packages.
import inspect
from bs4 import BeautifulSoup
# My modules.
import toolbox

# --- Globals. ---
find_a_grave = 'https://www.findagrave.com'
family_groups = ['parent', 'spouse', 'child', 'sibling', 'half-sibling']
family_groups_all = family_groups
family_groups_all.insert(0, 'burial')
family_groups_names = ['burials', 'parents', 'spouses', 'children', 
	'siblings', 'half-siblings']
data_groups_all = ['totals', 'names']
master_urls = []
master_list = 'master_list.txt'

cemetery_abreviation = {
	2353265 : 'PRES', # Sherrill Presbyterian Cemetery - Sherrill, Dubuque County, Iowa, USA
	2243718 : 'UCC',  # Sherrill United Church of Christ Cemetery - Sherrill, Dubuque County, Iowa, USA
	2145876 : 'SML',  # Saint Matthew Cemetery - Sherrill, Dubuque County, Iowa, USA
	1682503 : 'IOOF', # Sherrill United Methodist Church Cemetery - Sherrill, Dubuque County, Iowa, USA
	1676398 : 'SPP'   # Odd Fellows Cemetery - Sherrill, Dubuque County, Iowa, USA
}
cemetery = ['cemetery', 'Cemetery']
surname = ['surname', 'Surname']
name = ['name', 'Name']
nickname = ['nickname', 'Nickname']
id = ['id', 'ID']
birth = ['birth', 'Birth']
birth_location = ['birth_location', 'Birth Location']
death = ['death', 'Death']
death_location = ['death_location', 'Death Location']
parents_surname = ['parents_surname', 'Parent\'s Surname']
parents = ['parents', 'Parents']
spouses = ['spouses', 'Spouses']
father = ['father', 'Father']
mother = ['mother', 'Mother']
veteran = ['veteran', 'Veteran']
cenotaph = ['cenotaph', 'Cenotaph']
plot = ['plot', 'Plot']
bio = ['bio', 'Bio']
google_map = ['google_map', 'Google Map']
latitude = ['latitude', 'Latitude']
longitude = ['longitude', 'Longitude']
inscription = ['Inscription']
inscription = ['inscription', 'Inscription']
gravesite_details = ['gravesite_details', 'Gravesite Details']
notes = ['notes', 'Notes']
burial_type = ['burial_type', 'Burial Type']
row_data = [
	cemetery,
	surname,
	name,
	nickname,
	id,
	birth,
	birth_location,
	death,
	death_location,
	parents_surname,
	parents,
	spouses,
	father,
	mother,
	veteran,
	cenotaph,
	plot,
	bio,
	google_map,
	latitude,
	longitude,
	inscription,
	gravesite_details,
	notes,
	burial_type
]

# --- Functions. ---
def dig_instructions() :
	# --------------------------------------------
	# Return a dictionary of digging instructions.
	# Last update: 2024/05/28 @ 04:15pm.
	# --------------------------------------------

	# --- Vars. ---
	instructions = {}

	# --- Get lines from instructions file. ---
	lines = toolbox.get_instructions(1)  # Main is one level up, not here.
	if False == lines :
		quit()
	if 0 == len(lines) :
		toolbox.print_l('Error: no digging instructions.')
		quit()

	# --- Process lines. ---
	for line in lines :
		this_line = line.replace('\n', '').replace(' ', '')  # Clean & split.
		this_line = this_line.split(':')
		if 'log' == this_line[0] :
			toolbox.log()  # Start logging.
			continue
		if not this_line[0].isnumeric() :  # Invalid cemetery #?
			toolbox.print_l('Error: instructions - cemetery ' + this_line[0] + 
		 		' is non-numeric.')
			quit()

		# --- Check group for errors. ---
		# e.g. { 1682503 : [group, group] }
		called_by = inspect.stack()[1].filename.rsplit('/', 1)[1]
		groups = []
		if len(this_line) > 1 :  # There are one or more group(s)).
			groups = this_line[1].rstrip(',').split(',')  # Split them.
		else :  # No groups.
			groups = family_groups_all
			check_groups = family_groups_all

		# --- Remove duplicates. ---
		groups = list(dict.fromkeys(groups))  # Cool, huh?

		# --- Loop instruction groups. ---
		for group in groups :  
			if (group not in check_groups) :  # Valid group?
				toolbox.print_l('Error: instructions - invalid group "' + 
					group + '".')
				quit()
			# If "burial" is in groups, it must be the first list item.
			if 'burial' in groups and 'burial' != groups[0] :
				groups_before = groups
				groups_before.remove('burial')
				groups[0] = 'burial'
				groups.append(groups_before)

		# --- # Save to instructions dictionary. ---
		instructions.update({this_line[0]: groups})

	return instructions

def find_burial_urls(args) :
	# --------------------------------------------
	# Search cemetery index page(s) for memorial urls.
	# Sister function is find_family_urls().
	# Build an list file, return an array.
	# Last update: 2024/05/28 @ 10:30am.
	# --------------------------------------------

	# --- Define vars. ---
	session = args[0]
	cemetery_id = args[1]
	path_to_list = args[2]
	group = args[3]
	max_pages = 200
	page = 1
	loop = True
	memorial_urls = []
	toolbox.print_l()

	# --- Create group list. ---
	f = open(path_to_list[group], 'w')

	# --- Loop index pages. ---
	while (loop) :

		# --- Prevent runaways. ---
		if (page == max_pages) :  # 
			toolbox.print_l('Error: exceeded max (' + max_pages + ') pages.')
			quit()

		# --- Get index page. ---
		cemetery_index = find_a_grave + '/cemetery/' + cemetery_id 
		cemetery_index_page = cemetery_index + '/memorial-search?page=' + \
		str(page)  # Set page URL.
		request = toolbox.get_url(session, cemetery_index_page)  # Get page.

		# -- Make burial soup. --
		soup = BeautifulSoup(request.content, 'html.parser')

		# --- If last page, stop looping. ---
		# Search page tags for warnings.
		warnings = soup.find_all('span', {'class' : 'icon-warning'})
		for warning in warnings :  # Loop warnings.
			# No more pages?
			if warning.parent.text.lower().find('no matches found') > 0 :
				loop = False # No more pages.
				break
		if not loop :
			break
	
		# --- Find memorial pages. ---
		toolbox.print_l('Pulling "' + group + '" links from index ' + 
			cemetery_index_page)
		# Search page for memorial items.
		memorials = soup.find_all('div', {'class' : 'memorial-item'})
		# URL format: "https://www.findagrave.com/memorial/84600372/albert-mike-albrecht"

		# --- Loop memorial pages. ---
		for memorial in memorials : # Loop memorial items.
			if len(memorial.find_all('a')) > 0 : # Check if item has a link.
				memorial_url = find_a_grave + memorial.a['href']
				f.write(memorial_url + '\n') # Update burial list.
				memorial_urls.append(memorial_url)
		if (loop) :
			page += 1  # Increment page.
			toolbox.pause(0.5,2,True)  # Pace requests.
			toolbox.print_l('Next page.')

	# --- Finish. ---
	f.close()
	toolbox.remove_last_byte(f, path_to_list[group])  # Remove dangling "\n".
	if 0 == len(memorial_urls) :
		toolbox.print_l('Error: no memorials in cemetery ' + cemetery_id + '.')
		quit()
	else :
		toolbox.print_l('Done - (' + str(len(memorial_urls)) + ') links found.')
		return memorial_urls
	
def find_family_urls(group, this_soup) :
	# --------------------------------------------
	# Search memorial page soup for group (aka family) memorial URLs.
	# Sister function is find_burial_urls().
	# Return an array of memorial URLs.
	# Last update: 2024/05/28 @ 10:30am.
	# --------------------------------------------

	# --- Check input. ---
	if 'this_soup' not in locals():
		toolbox.print_l('Error: no Soup.')
		return False

	# --- Set element label for this group. ---
	family_urls = []
	match group:
		case 'parent':
			family = this_soup.find(id='parentsLabel')
		case 'spouse':
			family = this_soup.find(id='spouseLabel')
		case 'child':
			family = this_soup.find(id='childrenLabel')
		case 'sibling':
			family = this_soup.find(id='siblingLabel')
		case 'half-sibling':
			family = this_soup.find(id='halfSibLabel')
		case '' :
			toolbox.print_l('Error: no group.')
			return False
	
	# --- Find element in soup. ---
	if family is not None :
		family_links = family.parent.find_all('a')
		for family_link in family_links :
			family_url = find_a_grave + family_link['href']
			family_urls.append(family_url)

	return family_urls

def stash_group_page(args) :
	# --------------------------------------------
	# Save (aka stash) a group page.
	# Last update: 2024/05/28 @ 10:30am.
	# --------------------------------------------

	# --- Define vars. ---
	global master_urls
	session = args[0]
	group = args[1]
	burial_url = args[2]
	family_url = args[3]
	path_to_folder = args[4]
	if 'burial' == group :
		url = burial_url
	else :
		url = family_url

	# --- Request page. ---
	request = toolbox.get_url(session, url)
			
	# --- Set the stash file name. ---
	page = path_to_folder[group] + '/'
	burial_slug = burial_url.split('/memorial/')[1].replace('/', '_')
	if 'burial' == group :
		page = page + burial_slug
	else :
		family_slug = family_url.split('/memorial/')[1].replace('/', '_')
		page = page + family_slug + '_' + group + '-of_' + burial_slug
	
	# --- Stash the page. ---
	f = open(page + '.html', 'w')
	f.write(request.text)  # Stash page.
	f.close()

	# --- Add URL to master_urls dynamic list (Recreated with each group). ---
	if 'burial' == group :
		master_urls.append(burial_url)
	else :
		master_urls.append(family_url)

	# --- Pace requests. ---
	if 'burial' != group :
		toolbox.print_l('  ' + group + ' = "' + family_url + '"')
	pause_digging()

def pause_digging() :
	# --------------------------------------------
	# Random sleep when requesting web pages.
	# Last update: 2024/05/28 @ 10:30am.
	# --------------------------------------------

	# --- Pause. ---
	toolbox.pause(0.5,1,True)

def build_master_list(path_to_stash) :
	# --------------------------------------------
	# Prevent duplicating stashed pages. 
	# Create a list of all URLs for all cemeteries in this collection.
	# 1. For "path_to_stash" (aka collection), find all cemetery folders.
	# 2. Combine all group lists from all cemetery folders into a master list. 
	# 3. Master list is a snapshot of all URLs at _this_ point in time.
	# global master_urls[] is master list until saved by write_master_list().
	# Last update: 2024/05/28 @ 01:30pm.
	# --------------------------------------------

	# --- Define vars. ---
	global master_urls
	cemetery_folders = glob.glob(path_to_stash + '/*_*/')

	# --- Build a master list of all group lists. ---
	master_urls = []  # New list.
	for cemetery_folder in cemetery_folders :
		cemetery_id = cemetery_folder.split(path_to_stash)[1].split('_')[0]
		for group_name in family_groups_names :
			folder_name = cemetery_folder + cemetery_id + '_' + group_name
			list_name = folder_name + '_list.txt'
			if os.path.isfile(list_name) :
				f = open(list_name, 'r')
				urls = f.read().splitlines()
				f.close
				master_urls += urls

	return master_urls

def save_master_list(path_to_stash) :
	# --------------------------------------------
	# Write master list of URLs.
	# Last update: 2024/05/27 @ 12:00pm
	# --------------------------------------------

	# --- Save the master list. --
	f = open(path_to_stash + master_list, 'w')
	for url in master_urls :
		f.write(url + '\n')
	f.close()

def dig(burial_file_name, num_row) :
	# --------------------------------------------
	# Build a burial row for the output spreadsheet.
	# Last update: 2024/05/28 @ 10:30pm.
	# --------------------------------------------

	# --- Vars. ---
	cols_to_write = []

	# --- Fill the row. ---
	if 0 == num_row :
		# Header row.
		# Loop columns. Position [index][1] is column title.
		for index in range(len(row_data)) :
			cols_to_write.append(row_data[index][1])
	else:
		# Make burial soup.
		f = open(burial_file_name, 'r')
		soup = BeautifulSoup(f.read(), 'html.parser')
		f.close
		# Loop columns. Position [index][0] is switch match for dig_this()).
		for index in range(len(row_data)) :
			element = dig_this(soup, row_data[index][0])
			cols_to_write.append(element)

	return cols_to_write

def dig_this(this_soup, element) :
	# --------------------------------------------
	# Use Beautiful Soup library to find a data element.
	# Last update: 2024/05/29 @ 01:15pm.
	# --------------------------------------------

	# --- Check input. ---
	if 'this_soup' not in locals():
		toolbox.print_l('Error: no Soup.')
		return False
	
	# --- Find the script element which sets lots of vars. ---
	scripts = this_soup.find_all('script')
	for script in scripts :
		if None != script.string and \
			-1 != script.string.find('memorialCemeteryId') :
			break
	script_vars = script.string.split('\n')

	# --- Find data value. ---
	match element:
		case 'cemetery':
			element_id = 'memorialCemeteryId'
			cell_value = get_script_var_value(element_id, script_vars)
		case 'surname':
			element_id = 'lastName'
			cell_value = get_script_var_value(element_id, script_vars)
		case 'name':
			element_id = 'fullName'
			cell_value = get_script_var_value(element_id, script_vars)
		case 'nickname':
			cell_value = ''
		case 'id':
			element_id = 'personId'
			cell_value = get_script_var_value(element_id, script_vars)
		case 'birth':
			cell_value = ''
		case 'birth_location':
			location = this_soup.find(attrs={'itemprop': 'birthPlace'}).string
			cell_value = location.replace('\n', '').lstrip()
		case 'death':
			element_id = 'deathDate'
			cell_value = get_script_var_value(element_id, script_vars)
		case 'death_location':
			location = this_soup.find(attrs={'itemprop': 'deathPlace'}).string
			cell_value = location.replace('\n', '').lstrip()
		case 'parents_surname':
			cell_value = ''
		case 'parents':
			cell_value = ''
		case 'spouses':
			cell_value = ''
		case 'father':
			cell_value = ''
		case 'mother':
			cell_value = ''
		case 'veteran':
			cell_value = ''
		case 'cenotaph':
			element_id = 'isCenotaph'
			cell_value = get_script_var_value(element_id, script_vars)
		case 'plot':
			cell_value = this_soup.find(id='plotValueLabel').attrs['href']
		case 'bio':
			cell_value = ''
		case 'google_map':
			cell_value = this_soup.find(id='gpsValue').attrs['href']
		case 'latitude':
			cell_value = ''
		case 'longitude':
			cell_value = ''
		case 'inscription':
			cell_value = ''
		case 'gravesite_details':
			cell_value = ''
		case 'notes':
			cell_value = ''
		case 'burial_type':
			cell_value = ''
		case '' :
			toolbox.print_l('Error: no group.')
			cell_value = ''
	return cell_value

def get_script_var_value(var_id, vars) :
	# --------------------------------------------
	# Use Beautiful Soup library to find a data element.
	# Last update: 2024/05/29 @ 01:15pm.
	# --------------------------------------------

	# --- Return var. ---
	for var in vars :
		if var.find(var_id) > 0 :
			break
	var = var.split(':')[1]  # Split off the var string.
	double_quotes = re.search('".*"', var) # Does it use "?
	single_quotes = re.search('\'.*\'', var) # Does it use '?
	if None != double_quotes :
		var = double_quotes.group().replace('"', '').rstrip()
	if None != single_quotes :
		var = single_quotes.group().replace('"', '').replace(' ', '')
	if var.find('false,') :  # Boolean?
		var = False
	elif var.find('true,') :
		var = True
	return var
