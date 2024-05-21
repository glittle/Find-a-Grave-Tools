import requests
from bs4 import BeautifulSoup

# URL = "https://realpython.github.io/fake-jobs/"
# URL = "https://www.findagrave.com/cemetery/2243718/sherrill-united-church-of-christ-cemetery"
# URL = "https://www.findagrave.com/memorial/84600372/albert-mike-albrecht"
URL = "https://secure.findagrave.com/cgi-bin/fg.cgi?page=gr&GRid=84600372"

# https://stackoverflow.com/questions/73688432/python-request-with-cookies-content-blocked-by-cookie-banner
session = requests.Session()
headers = {
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'
}
session.headers.update(headers)
session.cookies.set("name", "notice_preferences", domain="www.findagrave.com/")
session.cookies.set( "value", "2:", domain="www.findagrave.com/")

url0 = 'https://www.findagrave.com/cemetery/2243718/memorial-search?cemeteryName=Sherrill%20United%20Church%20of%20Christ%20Cemetery&page=1#sr-84600372'
url1 = 'https://www.findagrave.com/memorial/84600372/albert-mike-albrecht'
url2='https://www.findagrave.com/memorial/84608940/annie-baal'

request = session.get(url0)
soup = BeautifulSoup(request.content, "html.parser")
print(soup.prettify)

def get_lat_long(url):
	request = session.get(url)
	soup = BeautifulSoup(request.content, "html.parser")
	location = soup.find(id="gpsValue")
	gmap = location.attrs['href']
	lat_long = location.attrs['href'].split('?')[1].split('&')[0].split('=')[1]
	return lat_long

mem_84600372 = get_lat_long(url1)
mem_84608940 = get_lat_long(url2)
	# lat=lat_long.split(',')[0]
	# long=lat_long.split(',')[1]

print("end")
