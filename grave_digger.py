# ------------------------------------------------\
#  Specific functions for find-a-grave-tools.
#  Last update: 2024/06/04 @ 03:15pm.
#
#  Name:               grave_digger.py
#  URI:                https://github.com/doug-foster/find-a-grave-tools
#  Description:	       Specific functions for find-a-grave-tools
#  Version:		       1.1.1
#  Requires at least:  3.1 Python
#  Prefers:            3.12 Python
#  Author:             Doug Foster
#  Author URI:         http://dougfoster.me
#  License:            GPL v3 or later
#  License URI:        https://www.gnu.org/licenses/agpl-3.0.html
#  Update URI:         https://github.com/doug-foster/find-a-grave-tools
#  Text Domain:        find-a-grave-tool
# ------------------------------------------------\

# --- Import libraries. ---
# Standard Libraries.
import os  # https://docs.python.org/3/library/os.html
import glob  # https://docs.python.org/3/library/glob.html
import re  # https://docs.python.org/3/library/re.html
import inspect  # https://docs.python.org/3/library/inspect.html
from urllib.parse import unquote  # https://docs.python.org/3/library/urllib.html
# Packages.
from bs4 import BeautifulSoup  # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# My modules.
import toolbox  # https://github.com/doug-foster/find-a-grave-tools

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
lat_long = None
cemetery_folders = []
g_map = ''
cemetery = ['cemetery', 'Cemetery']
surname = ['surname', 'Surname']
name = ['name', 'Name']
id = ['id', 'ID']
birth = ['birth', 'Birth']
birth_location = ['birth_location', 'Birth Location']
death = ['death', 'Death']
death_location = ['death_location', 'Death Location']
parents_surname = ['parents_surname', 'Parent\'s Surname']
parents = ['parents', 'Parents']
father = ['father', 'Father']
mother = ['mother', 'Mother']
spouses = ['spouses', 'Spouses']
children = ['children', 'Children']
siblings = ['siblings', 'Siblings']
half_siblings = ['half_siblings', 'Half-siblings']
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
row_data = [
	cemetery,
	surname,
	name,
	id,
	birth,
	birth_location,
	death,
	death_location,
	parents_surname,
	parents,
	father,
	mother,
	spouses,
	children,
	siblings,
	half_siblings,
	veteran,
	cenotaph,
	plot,
	bio,
	google_map,
	latitude,
	longitude,
	inscription,
	gravesite_details
]

# --- Functions. ---
# dig_instructions()
# find_burial_urls(args)
# find_family_urls(group, soup)
# stash_group_page(args)
# pause_digging()
# build_master_list(path_to_stash)
# save_master_list(path_to_stash)
# dig(args)
# dig_this(args)
# get_by_group(soup, group)
# build_link(url, text)
# lat_long(which, gmap_url='')
# adjust_worksheet(worksheet)
# soup_find(soup, what, type, value=)
# parent_surname(soup, mem_url)


# --------------------------------------------\
#  Return a dictionary of digging instructions.
#  Last update: 2024/06/03 @ 08:45am.
# --------------------------------------------\
def dig_instructions() :

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
# --------------------------------------------/


# --------------------------------------------\
#  Search cemetery index page(s) for memorial urls.
#  Last update: 2024/06/03 @ 08:45am.
#
#  Sister function is find_family_urls().
#  Build an list file, return an array.
# --------------------------------------------\
def find_burial_urls(args) :

	# --- Define vars. ---
	session = args[0]
	cemetery_id = args[1]
	path_to_list = args[2]
	group = args[3]
	max_pages = 200
	page = 1
	loop = True
	memorial_urls = []
	# toolbox.print_l()

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
		warnings = soup_find(soup, 'warnings')
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
		memorials = soup_find(soup, 'memorials')
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
# --------------------------------------------/	


# --------------------------------------------\
#  Search memorial page soup for group (aka family) memorial URLs.
#  Last update: 2024/06/03 @ 08:45am.
#
#  Sister function is find_burial_urls().
#  Return an array of memorial URLs.
#  Used by stash_graves.py.
#  NOT used by dig_graves.py.
# --------------------------------------------\
def find_family_urls(group, soup) :

	# --- Vars. ---
	family_urls = []

	# --- Check input. ---
	if 'soup' not in locals():
		toolbox.print_l('Error: no Soup.')
		return False

	# --- Set element label for this group. ---
	family = soup_find(soup, group)
	if 0 == len(family) : return ''
	
	# --- Find element in soup. ---
	family_links = family.parent.find_all('a')
	for family_link in family_links :
		family_url = find_a_grave + family_link['href']
		family_urls.append(family_url)

	return family_urls
# --------------------------------------------/


# --------------------------------------------\
#  Save (aka stash) a group page.
#  Last update: 2024/06/03 @ 08:45am.
# --------------------------------------------\
def stash_group_page(args) :

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
# --------------------------------------------/


# --------------------------------------------\
#  Random sleep when requesting web pages.
#  Last update: 2024/06/03 @ 08:45am.
# --------------------------------------------\
def pause_digging() :

	# --- Pause. ---
	toolbox.pause(0.5,1,True)
# --------------------------------------------/


# --------------------------------------------\
#  Prevent duplicating stashed pages.
#  Last update: 2024/06/03 @ 08:45am.
#
#  Create a list of all URLs for all cemeteries in this collection
#  1. For "path_to_stash" (aka collection), find all cemetery folders
#  2. Combine all group lists from all cemetery folders into a master list 
#  3. Master list is a snapshot of all URLs at _this_ point in time.
#
#  global master_urls[] is master list until saved by write_master_list().
# --------------------------------------------\
def build_master_list(path_to_stash) :

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
# --------------------------------------------/


# --------------------------------------------\
#  Write master list of URLs.
#  Last update: 2024/06/03 @ 08:45am.
# --------------------------------------------\
def save_master_list(path_to_stash) :

	# --- Save the master list. --
	f = open(path_to_stash + master_list, 'w')
	for url in master_urls :
		f.write(url + '\n')
	f.close()
# --------------------------------------------/


# --------------------------------------------\
#  Build a burial row for the output spreadsheet.
#  Last update: 2024/06/03 @ 08:45am.
# --------------------------------------------\
def dig(args) :

	# --- Vars. ---
	burial_file_name = args[0]
	num_row = args[1]
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
			args = [soup, row_data[index][0]]
			element = dig_this(args)
			cols_to_write.append(element)

	return cols_to_write
# --------------------------------------------/


# --------------------------------------------\
#  Use Beautiful Soup library to find a data element.
#  Last update: 2024/06/03 @ 12:30pm.
# --------------------------------------------\
def dig_this(args) :

	# --- Vars. ---
	soup = args[0]
	element = args[1]
	cell_value = ''
	element_value = ''
	global lat_long
	global g_map

	# --- Check input. ---
	if 'soup' not in locals():
		toolbox.print_l('Error: no Soup.')
		return False

	# --- Find data value. ---
	match element:
		case 'cemetery':
			cemetery_url = soup_find(soup, 'cemetery')
			cemetery_id = cemetery_url.split('/')[2]
			full_url = find_a_grave + cemetery_url
			element_value = build_link(full_url, cemetery_id)
			cell_value = element_value
		case 'surname':
			mem_url = soup_find(soup, 'mem_url')
			parts = mem_url.split('/')
			this_name_string = parts[len(parts)-1]
			parts = re.split('-|_', this_name_string)  # Delimiter could be '-' or '_'.
			element_value = unquote(parts[len(parts)-1].capitalize())
			cell_value = element_value
		case 'name':
			element_value = soup_find(soup, 'full_name')
			cell_value = element_value
		case 'id':
			memorial_id = soup_find(soup, 'mem_id')
			full_url = find_a_grave + '/memorial/' + memorial_id
			element_value = build_link(full_url, memorial_id)
			cell_value = element_value
		case 'birth':
			element_value = soup_find(soup, 'birth')
			cell_value = element_value
		case 'birth_location':
			element_value = soup_find(soup, 'birth_location')
			cell_value = element_value
		case 'death':
			element_value = soup_find(soup, 'death')
			cell_value = element_value
		case 'death_location':
			element_value = soup_find(soup, 'death_location')
			cell_value = element_value
		case 'parents_surname':
			mem_url = soup_find(soup, 'mem_url')
			element_value = parent_surname(soup, mem_url)
			cell_value = element_value
		case 'parents':
			element_value = get_by_group(soup, 'parents')
			cell_value = element_value
		case 'father':
			element_value = get_by_group(soup, 'father')
			cell_value = element_value
		case 'mother':
			element_value = get_by_group(soup, 'mother')
			cell_value = element_value
		case 'spouses':
			element_value = get_by_group(soup, 'spouses')
			cell_value = element_value
		case 'children':
			element_value = get_by_group(soup, 'children')
			cell_value = element_value
		case 'siblings':
			element_value = get_by_group(soup, 'siblings')
			cell_value = element_value
		case 'half_siblings':
			element_value = get_by_group(soup, 'half-siblings')
			cell_value = element_value
		case 'veteran':
			element_value = soup_find(soup, 'veteran')
			cell_value = element_value
		case 'cenotaph':
			element_value = soup_find(soup, 'cenotaph')
			cell_value = element_value
		case 'plot':
			element_value = soup_find(soup, 'plot')
			cell_value = element_value
		case 'bio':
			element_value = soup_find(soup, 'bio')
			cell_value = element_value
		case 'google_map':
			g_map = soup_find(soup, 'google_map')
			element_value = build_link(g_map, 'map')
			cell_value = element_value
		case 'latitude':
			element_value = lat_long('lat', g_map)
			cell_value = element_value
		case 'longitude':
			element_value = lat_long('long', g_map)
			cell_value = element_value
		case 'inscription':
			element_value = soup_find(soup, 'inscription')
			cell_value = element_value
		case 'gravesite_details':
			element_value = soup_find(soup, 'gravesite-details')
			cell_value = element_value
		case '' :
			toolbox.print_l('Error: no group.')
			cell_value = ''
	return cell_value
# --------------------------------------------/


# --------------------------------------------\
#  Create ouput for family groups. 
#  Last update: 2024/06/04 @ 01:30pm.
# --------------------------------------------\
def get_by_group(soup, group, value='') :

	# --- Find soup objects by this group. ---
	match group :
		case 'parents' :
			people = soup_find(soup, 'parents')
		case 'num_parents' :
			people = soup_find(soup, 'parents')
		case 'father' :	
			people = soup_find(soup, 'parents')
		case 'mother' :
			people = soup_find(soup, 'parents')
		case 'spouses' :
			people = soup_find(soup, 'spouses')
		case 'children' :
			people = soup_find(soup, 'children')		
		case 'siblings' :
			people = soup_find(soup, 'siblings')
		case 'half-siblings' :
			people = soup_find(soup, 'half-siblings')
	if 0 == len(people) : return ''

	# --- # of parents are used to determine surname.
	if 'num_parents' == group :
		return (len(people))

	# --- Loop family group members. ---
	if 'father' == group or 'mother' == group :
		parents = []
		for person in people :
			parent = []
			name = soup_find('', 'person_name', '', person)
			url = soup_find(soup, 'person_url', '', person)
			if '' != url : find_a_grave + url
			parent.append(url)
			parent.append(name)
			parents.append(parent)
	else :
		output = ''
		for person in people :
			name = soup_find('', 'person_name', '', person)
			birth = soup_find(soup, 'person_birth', '', person)
			death = soup_find(soup, 'person_death', '', person)
			#  Will always have a name, may/not have birth & death.
			if '' != birth and '' != death :
				output += name + ', ' + birth + ' - ' + death + '\n'
			elif '' != birth and '' == death :
				output += name + ', ' + birth + '\n'
			elif '' == birth and '' != death :
				output += name + ', ' + birth + '\n'

	# --- For a family group, create output. ---
	if 'father' == group or 'mother' == group :
		match len(parents) :
			case 0 :  # if no parents, return ''
				return ''
			case 1 :  # If one parents, use the same url for both father and mother.
				return build_link(parents[0][0], parents[0][1])
			case 2 :  # If two parents, order is always father, mother.
				if 'father' == group :
					return build_link(parents[0][0], parents[0][1])
				if 'mother' == group :
					return build_link(parents[1][0], parents[1][1])
			case _ : return 'More than two parents.'

	else :
		return output[:-1]  # Remove last '\n'.		
# --------------------------------------------/


# -------------------------------------------\
#  Return a list of items to create a hyperlink.
#  Last update: 2024/06/04 @ 01:00pm.
# -------------------------------------------\
def build_link(url, text) :

	# --- Check input. ---
	if '' == url :
		return ''
	
	# --- Vars. ---
	item = []

	# --- Return item list. ---
	item.append('url')
	item.append(url)
	item.append(text)
	return item
# -------------------------------------------/


# -------------------------------------------\
#  Return lattitude & longitude from a Google Map URL
#  Last update: 2024/06/03 @ 08:45am.
# -------------------------------------------\
def lat_long(which, gmap_url='') :

	# --- Check input. ---
	if '' == gmap_url :
		return ''
	
	# --- Check input. ---
	if None != re.search('edit', gmap_url) : return ''
	lat_long = re.search('(?<=q=)..*(?=&)', gmap_url).group().split(',')
	if None == lat_long : return ''

	# --- Return values. ---
	if 'lat' == which :
		return lat_long[0]
	if 'long' == which :
		return lat_long[1]
# --------------------------------------------/


# --------------------------------------------\
#  Final worksheet tweaks
#  Last update: 2024/06/03 @ 08:45am.
# --------------------------------------------\
def adjust_worksheet(worksheet) :
	
	# --- Find column position. ---
	for i in range(len(row_data)) :
		if row_data[i][0] == 'birth_location' :
			birth = i
			break
	for i in range(len(row_data)) :
		if row_data[i][0] == 'death_location' :
			death = i
			break
	for i in range(len(row_data)) :
		if row_data[i][0] == 'bio' :
			bio = i
			break
	for i in range(len(row_data)) :
		if row_data[i][0] == 'inscription' :
			inscription = i
			break
	for i in range(len(row_data)) :
		if row_data[i][0] == 'gravesite_details' :
			gravesite_details = i
			break
	
	# --- Make worksheet adjustments. ---
	worksheet.autofit()
	worksheet.freeze_panes(1, 0)
	worksheet.set_column(birth, birth, 35)
	worksheet.set_column(death, death, 35)
	worksheet.set_column(bio, bio, 40)
	worksheet.set_column(inscription, inscription, 40)
	worksheet.set_column(gravesite_details, gravesite_details, 40)
# --------------------------------------------/


# --------------------------------------------\
#  Use Beautiful Soup library to find data element(s).
#  Last update: 2024/06/04 @ 03:15pm.
# --------------------------------------------\
def soup_find(soup, what, type='', value='') :

	match what :
		case 'warnings' :
			cup_of_soup = soup.find_all('span', {'class' : 'icon-warning'})
			if None == cup_of_soup : return ''
			else : return cup_of_soup
		case 'memorials' :
			cup_of_soup = soup.find_all('div', {'class' : 'memorial-item'})
			if None == cup_of_soup : return ''
			else : return cup_of_soup
		case 'cemetery' :
			item = soup.find(id='cemeteryNameLabel').parent
			if None == item : return ''
			else : return item.get('href')
		case 'full_name' :  # aka surname, name, parents_surname
			item = soup.find(id='bio-name')
			if None == item : return ''
			else : return toolbox.clean_string(item.text)
		case 'mem_url' :
			item = soup.head.find(attrs={'rel' : 'canonical'})
			if None == item : return ''
			else : return item.get('href')
		case 'mem_id' :  # aka id
			item = soup.find(id='memNumberLabel')
			if None == item : return ''
			else : return toolbox.clean_string(item.text)
		case 'birth' :
			item = soup.find(id='birthDateLabel')
			if None == item : return ''
			else : return toolbox.clean_string(item.text)
		case 'birth_location' :
			item = soup.find(id='birthLocationLabel')
			if None == item : return ''
			else : return toolbox.clean_string(item.text)
		case 'death' :
			item = soup.find(id='deathDateLabel')
			if None == item : return ''
			else : return toolbox.clean_string(item.text)
		case 'death_location' :
			item = soup.find(id='deathLocationLabel')
			if None == item : return ''
			else : return toolbox.clean_string(item.text)
		case 'parents' :
			label = '[aria-labelledby="parentsLabel"] li [itemprop="name"]'
			cup_of_soup = soup.select(label)
			if None == cup_of_soup : return ''
			return cup_of_soup
		case 'person_name' :
			if value == None : return ''
			else : return toolbox.clean_string(value.text)
		case 'person_url' :
			item = value.parent.parent
			if None == item : return ''
			else : return item['data-href']
		case 'person_birth' :
			item = value.parent.find(id="familyBirthLabel")
			if None == item : return ''
			else : return toolbox.clean_string(item.text)
		case 'person_death' :
			item = value.parent.find(id="familyDeathLabel")
			if None == item : return ''
			else : return toolbox.clean_string(item.text)
		case 'spouses' :
			label = '[aria-labelledby="spouseLabel"] li [itemprop="name"]'
			cup_of_soup = soup.select(label)
			if None == cup_of_soup : return ''
			return cup_of_soup
		case 'children' :
			label = '[aria-labelledby="childrenLabel"] li [itemprop="name"]'
			cup_of_soup = soup.select(label)
			if None == cup_of_soup : return ''
			return cup_of_soup
		case 'siblings' :
			label = '[aria-labelledby="siblingLabel"] li [itemprop="name"]'
			cup_of_soup = soup.select(label)
			if None == cup_of_soup : return ''
			return cup_of_soup
		case 'half-siblings' :
			label = '[aria-labelledby="halfSibLabel"] li [itemprop="name"]'
			cup_of_soup = soup.select(label)
			if None == cup_of_soup : return ''
			return cup_of_soup	
		case 'veteran' :
			item = soup.select('h1 .icon-vet')
			if 0 == len(item) : return ''
			else : return 'Y'
		case 'cenotaph' :
			item = soup.find(id='cemeteryLabel')
			if None == item : return ''
			else :
				value = ''
				if 'cenotaph' == item.text.lower() : value = 'Y'
				return value
		case 'plot' :
			item = soup.find(id='plotValueLabel')
			if None == item : return ''
			else : return toolbox.clean_string(item.text)
		case 'bio' :
			item = soup.find(id='partBio')
			if None == item : return ''
			else : return toolbox.clean_string(str(item))
		case 'google_map' :
			item = soup.find(id='gpsValue')
			if None == item : return ''
			else :
				# Check if no GPS values.
				if -1 != item.get('href').find('edit#') : return ''
				else : return item.get('href')
		case 'inscription':
			item = soup.find(id='inscriptionValue')
			if None == item : return ''
			else : return toolbox.clean_string(str(item))
		case 'gravesite_details':
			item = soup.find(id='gravesite-details')
			if None == item : return ''
			else : return toolbox.clean_string(str(item))
		case 'by_attr' :
			cup_of_soup = soup.find(attrs={type: value})
			return cup_of_soup
	return ''
# --------------------------------------------/


# --------------------------------------------\
#  Parent surname.
#  Last update: 2024/06/04 @ 12:15pm.
# --------------------------------------------\
def parent_surname(soup, mem_url) :

	# --- Last name for this person. ---
	parts = mem_url.split('/')
	this_name_string = parts[len(parts)-1]
	parts = re.split('-|_', this_name_string)  # Delimiter could be '-' or '_'.
	this_last_name = parts[len(parts)-1]  # Lower case.

	# --- Last name for this father. ---
	father = get_by_group(soup, 'father')
	if '' == father : father_last_name = ''
	else :
		father_url = father[1]
		parts = father_url.split('/')
		father_name_string = parts[len(parts)-1]
		parts = re.split('-|_', father_name_string)  # Delimiter could be '-' or '_'.
		father_last_name = parts[len(parts)-1]  # Lower case.

	# --- Choose surname based on number of parents. ---
	num_parents = get_by_group(soup, 'num_parents')
	match num_parents :
		case 0: return ''
		case 1:
			if this_last_name == father_last_name :
				return unquote(this_last_name.capitalize())
			else : return ''
		case 2: return unquote(father_last_name.capitalize())
		case _: return ''
# --------------------------------------------/

# ------------------------------------------------/
