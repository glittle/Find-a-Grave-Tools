import os
dir = 'data/2243718_sherrill-united-church-of-christ-cemetery/'
files = os.listdir(dir)
for file in files :
	os.rename(dir + file, dir + file.replace('_page', ''))