# Find a Grave scraper
Pull, stash, extract, analyze, and report data for 'Find a Grave' (https://www.findagrave.com) memorial pages.
## Last updated
2024-05-28

## Background
These python scripts were created to help Cindy Foster @ iHuntDeadPeople.com with [one of her genealogy research projects](https://ihuntdeadpeople.com/let-us-help-with-your-genealogy-research/).

Cindy is creating a book about the five protestant cemeteries in Sherrill, Iowa. The book catalogs all of the burials in those cemeteries (as well as connected family burials). Additionally, her book presents a collection of data and stories around the lives of those people.

You can read more about Cindy and her work at https://ihuntdeadpeople.com/about/

## Description
Unfortunately 'Find a Grave' does not expose a public [API](https://en.wikipedia.org/wiki/API) to programatically extract information. If we want to mine data from the website for a genealogy project, we have to [scrape](https://en.wikipedia.org/wiki/Web_scraping) pages.

Rather than continously hit live website pages for data, pages needed for a project are pulled and then stashed locally. The analysis script(s) use these stashed pages.

stash_graves.py is used to:
- PULL specific pages for specifc groups in a collection of cemeteries.
	- An instruction file contains the cemeteries and groups to pull.
	- Cemeteries are identified by the same numeric ID 'Find a Grave' uses. 
	- Groups are: burial, parent, spouse, child, sibling, half-sibling
- STASH the pulled pages in a local directory (much like how a cache works).

dig_graves.py is used to:
- EXTRACT the data
	- Leverages the [Beautiful Soup](https://pypi.org/project/beautifulsoup4/) Python package
- ANALYZE the data
- REPORT data to a saved Excel spreadsheet
	- Uses the [XlsxWriter](https://pypi.org/project/XlsxWriter/) Python package

## Further development
As mentioned earlier, these scripts were written for a specific project. They are not intended to be an open-source project. Please use them as-is and do not expect on-going support or updates. Hopefully though they will provide you with inspiration for your own versions.
## License
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

A copy of the GNU General Public License is [included](LICENSE.txt) in this repository. Please also refer to https://www.gnu.org/licenses/.
## About me
You can lern more about the developer at https://dougfoster.me.
