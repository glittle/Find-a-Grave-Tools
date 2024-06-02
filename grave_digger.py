# ------------------------------------------------\
#  Specific functions for find-a-grave-scraper.
#  Last update: 2024/06/02 @ 12:45am.
#
#  Name:              grave_digger.py
#  URI:               https://github.com/doug-foster/find-a-grave-scraper
#  Description:	      Specific functions for find-a-grave-scraper
#  Version:		      1.00
#  Requires at least: 3.1
#  Requires Python:   3.12
#  Author:            Doug Foster
#  Author URI:        http://dougfoster.me
#  License:           GPL v3 or later
#  License URI:       https://www.gnu.org/licenses/agpl-3.0.html
#  Update URI:        https://github.com/doug-foster/find-a-grave-scraper
#  Text Domain:       find-a-grave-scraper
# ------------------------------------------------\

# --- Import libraries. ---
# Standard Libraries.
import os  # https://docs.python.org/3/library/os.html
import glob  # https://docs.python.org/3/library/glob.html
import re  # https://docs.python.org/3/library/re.html
import inspect  # https://docs.python.org/3/library/inspect.html
# Packages.
from bs4 import BeautifulSoup  # https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# My modules.
import toolbox  # https://github.com/doug-foster/find-a-grave-scraper

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
# find_family_urls(group, this_soup)
# stash_group_page(args)
# pause_digging()
# build_master_list(path_to_stash)
# save_master_list(path_to_stash)
# dig(args)
# dig_this(args)
# get_by_script_var_value(var_id, vars)
# get_by_attr(attr_type, attr_value, this_soup, type='text')
# get_by_group_label(label, this_soup, type='text')
# build_link(url, text)
# lat_long(which, gmap_url='')
# adjust_worksheet(worksheet)
# get_surname()

# --------------------------------------------\
#  Return a dictionary of digging instructions.
#  Last update: 2024/05/28 @ 04:15pm.
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
#  Last update: 2024/05/28 @ 10:30am.
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
# --------------------------------------------/	


# --------------------------------------------\
#  Search memorial page soup for group (aka family) memorial URLs.
#  Last update: 2024/05/28 @ 10:30am.
#
#  Sister function is find_burial_urls().
#  Return an array of memorial URLs.
# --------------------------------------------\
def find_family_urls(group, this_soup) :

	# --- Vars. ---
	family_urls = []

	# --- Check input. ---
	if 'this_soup' not in locals():
		toolbox.print_l('Error: no Soup.')
		return False

	# --- Set element label for this group. ---
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
	if None == family : return ''
	
	# --- Find element in soup. ---
	family_links = family.parent.find_all('a')
	for family_link in family_links :
		family_url = find_a_grave + family_link['href']
		family_urls.append(family_url)

	return family_urls
# --------------------------------------------/


# --------------------------------------------\
#  Save (aka stash) a group page.
#  Last update: 2024/05/28 @ 10:30am.
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
#  Last update: 2024/05/28 @ 10:30am.
# --------------------------------------------\
def pause_digging() :

	# --- Pause. ---
	toolbox.pause(0.5,1,True)
# --------------------------------------------/


# --------------------------------------------\
#  Prevent duplicating stashed pages.
#  Last update: 2024/05/28 @ 01:30pm.
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
#  Last update: 2024/05/27 @ 12:00pm
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
#  Last update: 2024/05/29 @ 04:30pm.
# --------------------------------------------\
def dig(args) :

	# --- Vars. ---
	burial_file_name = args[0]
	num_row = args[1]
	path_to_stash = args[2]
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
			args = [soup, row_data[index][0], path_to_stash]
			element = dig_this(args)
			cols_to_write.append(element)

	return cols_to_write
# --------------------------------------------/


# --------------------------------------------\
#  Use Beautiful Soup library to find a data element.
#  Last update: 2024/06/02 @ 12:30am.
# --------------------------------------------\
def dig_this(args) :

	# --- Vars. ---
	this_soup = args[0]
	element = args[1]
	path_to_stash = args[2]
	cell_value = ''
	global lat_long
	global g_map

	# --- Check input. ---
	if 'this_soup' not in locals():
		toolbox.print_l('Error: no Soup.')
		return False

	# --- Find the script element which sets lots of vars. ---
	scripts = this_soup.find_all('script')
	for script in scripts :
		if script.string :
			if -1 != script.string.find('memorialCemeteryId') :
				script_vars = script.string.split('\n')
	if None == script_vars :
		toolbox.print_l('Error: no script vars (memorialCemeteryId)')

	# --- Find data value. ---
	match element:
		case 'cemetery':
			cemetery_id = get_by_script_var_value('memorialCemeteryId', \
										 script_vars)
			url = find_a_grave + '/cemetery/' + cemetery_id
			cell_value = build_link(url, cemetery_id)
		case 'surname':
			cell_value = get_by_script_var_value('lastName', script_vars)
		case 'name':
			cell_value = get_by_script_var_value('fullName', script_vars)
		case 'id':
			memorial_id = get_by_script_var_value('memorialId', script_vars)
			url = find_a_grave + '/memorial/' + memorial_id
			cell_value = build_link(url, memorial_id)
		case 'birth':
			cell_value = get_by_attr('id','birthDateLabel', this_soup)
		case 'birth_location':
			cell_value = get_by_attr('itemprop','birthPlace', this_soup)
		case 'death':
			cell_value = get_by_script_var_value('deathDate', script_vars)
		case 'death_location':
			cell_value = get_by_attr('itemprop','deathPlace', this_soup)
		case 'parents_surname':
			cell_value = get_surname(this_soup, script_vars)
		case 'parents':
			cell_value = get_by_group_label('parentsLabel', this_soup)
		case 'father':
			cell_value = get_by_group_label('parentsLabel', this_soup, \
				type='father')
		case 'mother':
			cell_value = get_by_group_label('parentsLabel', this_soup, \
				type='mother')
		case 'spouses':
			cell_value = get_by_group_label('spouseLabel', this_soup)
		case 'children':
			cell_value = get_by_group_label('childrenLabel', this_soup)
		case 'siblings':
			cell_value = get_by_group_label('siblingLabel', this_soup)
		case 'half-siblings':
			cell_value = get_by_group_label('halfSibLabel', this_soup)
		case 'veteran':
			cell_value = get_by_attr('-','-', this_soup, 'vet')
		case 'cenotaph':
			cell_value = get_by_script_var_value('isCenotaph', script_vars)
		case 'plot':
			cell_value = get_by_attr('id','plotValueLabel', this_soup)
		case 'bio':
			cell_value = get_by_attr('id','partBio', this_soup)
		case 'google_map':
			g_map = get_by_attr('id','gpsValue', this_soup, 'soup').attrs['href']
			cell_value = build_link(g_map, 'map')
		case 'latitude':
			cell_value = lat_long('lat', g_map)
		case 'longitude':
			cell_value = lat_long('long', g_map)
		case 'inscription':
			cell_value = get_by_attr('id','inscriptionValue', this_soup)
		case 'gravesite_details':
			cell_value = get_by_attr('id', 'gravesite-details', this_soup)
		case '' :
			toolbox.print_l('Error: no group.')
			cell_value = ''
	return cell_value
# --------------------------------------------/


# --------------------------------------------\
#  Use Beautiful Soup library to find a data element.
#  Last update: 2024/06/01 @ 06:45pm.
# --------------------------------------------\
def get_by_script_var_value(var_id, vars) :

	# --- Return var value. ---
	for var in vars :
		if var.find(var_id) > 0 :
			break
	var = var.split(':')[1]  # Split off the var string.
	double_quotes = re.search('".*"', var) # Does it use "?
	single_quotes = re.search('\'.*\'', var) # Does it use '?
	if None != double_quotes :
		var = double_quotes.group().replace('"', '').rstrip()
	if None != single_quotes :
		var = single_quotes.group().replace('\'', '').replace(' ', '')
	if var.find('true,') > 0 :
		var = 'Y'
	elif var.find('false,') > 0 :
		var = ''
	var = toolbox.clean_string(var)
	return var
# --------------------------------------------/


# --------------------------------------------\
#  Use Beautiful Soup library to find a data element.
#  Last update: 2024/06/02 @ 12:45am.
# --------------------------------------------\
def get_by_attr(attr_type, attr_value, this_soup, type='text') :

	# --- Vars. ---
	output = ''
	before = ''

	if 'vet' == type :
		vet = this_soup.select('h1 .icon-vet')
		if len(vet) > 0 : return 'Y'
		else : return ''

	# --- Find the correct attributes. ---
	if 'id' == attr_type :
		target = this_soup.find(id=attr_value)
	elif 'class' == attr_type :
		target = this_soup.find(class_=attr_value)
	else :
		target = this_soup.find(attrs={attr_type: attr_value})
	if None == target : return ''

	# --- Return soup object.
	if 'soup' == type :
		return target
	
	# --- Return output string. ---
	if 1 == len(target.contents) :  # One element.
		output = toolbox.clean_string(target.text)
	else :  # Multiple elements.
		for i in range(len(target.contents)) :
			before += str(target.contents[i])
		# Change html elements to text string.
		output = toolbox.clean_string(output)
	return output
# --------------------------------------------/


# --------------------------------------------\
#  Use Beautiful Soup library to find a multiple elements for a group.
#  Last update: 2024/06/01 @ 11:30pm.
# --------------------------------------------\
def get_by_group_label(label, this_soup, type='text') :

	# --- Vars. ---
	find_name = '[aria-labelledby="' + label + '"] li [itemprop="name"]'
	output = ''
	parent = []
	parents = []

	# --- Find soup objects with this label. ---
	people = this_soup.select(find_name)
	if None == people : return ''

	# --- # of parents are used to determine surname.
	if 'num_parents' == type and 'parentsLabel' == label :
		return (len(people))

	# --- For a family group, set text output. ---
	# Case scenarios:
	#  parentsLabel(type='text')
	#  spouseLabel(type='text')
	#  childrenLabel(type='text')
	#  siblingLabel(type='text')
	#  halfSibLabel(type='text')
	if 'text' == type :
		i = 0
		for person in people :
			# Get/set name.
			name = toolbox.clean_string(person.text)
			# Get/set birth date.
			birth_date = person.parent.find(id="familyBirthLabel")
			if None == birth_date : birth = ''
			else : birth = birth_date.text
			# Get/set death date.
			death_date = person.parent.find(id="familyDeathLabel")
			if None == death_date : death = ''
			else : death = death_date.text

			#  Will always have name, may/not have birth & death.
			if '' != birth and '' != death :
				output += name + ', ' + birth + ' - ' + death + '\n'
			elif '' != birth and '' == death :
				output += name + ', ' + birth + '\n'
			elif '' == birth and '' != death :
				output += name + ', ' + birth + '\n'
		return output[:-1]

	# --- For mother/father, set URL output. ---
	# Case scenarios:
	#  parentsLabel(type='father')
	#  parentsLabel(type='mother')

	# Get name & URL for each parent.
	for person in people :
		url = person.parent.parent['data-href']
		if None == url : url = ''
		else : url = find_a_grave + url
		parent.append(url)
		parent.append(toolbox.clean_string(person.text))
		parents.append(parent)
		parent = []

	# Build URL for this parent.
	match len(parents) :
		case 0 :  # if no parents, return ''
			return ''
		case 1 :  # If one parents, use the same url for both father and mother.
			return build_link(parents[0][0], parents[0][1])
		case 2 :  # If two parents, order is always father, mother.
			if 'father' == type :
				return build_link(parents[0][0], parents[0][1])
			if 'mother' == type :
				return build_link(parents[1][0], parents[1][1])
# --------------------------------------------/


# -------------------------------------------\
#  Return a list of items to create a hyperlink.
#  Last update: 2024/05/30 @ 01:00pm.
# -------------------------------------------\
def build_link(url, text) :

	# --- Vars. ---
	item = []
	link = [item]

	# --- Return link item list. ---
	item.append('url')
	item.append(url)
	item.append(text)
	return item
# -------------------------------------------/


# -------------------------------------------\
#  Return lattitude & longitude from a Google Map URL
#  Last update: 2024/06/01 @ 07:45pm.
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
#  Last update: 2024/06/01 @ 09:00pm.
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
#  Return surname.
#  Last update: 2024/06/01 @ 09:00pm.
# --------------------------------------------\
def get_surname(this_soup, script_vars) :

	# --- Last names for this person & father. ---
	this_name = get_by_script_var_value('fullName', script_vars)
	this_last_name = this_name.rsplit(' ', 1)[1]
	father_name = get_by_group_label('parentsLabel', this_soup, type='father')
	if '' == father_name : 
		father_last_name = ''
	else :
		father_last_name = father_name[2].rsplit(' ', 1)[1]

	# Surname based on number of parents.
	match get_by_group_label('parentsLabel', this_soup, type='num_parents') :
		case 0:
			return ''
		case 1:
			if this_last_name == father_last_name : return this_last_name
			else : return ''
		case 2:
			return father_last_name
	return ''
# --------------------------------------------/

# ------------------------------------------------/

