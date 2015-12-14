#!/bin/python
import os
import re
import sys
import argparse
import getopt
import requests
import webbrowser
# import MySQLdb
import cPickle as pickle
import time
from bs4 import BeautifulSoup

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
   	'Accept-Encoding': 'none',
   	'Accept-Language': 'en-US,en;q=0.8',
   	'Connection': 'keep-alive'
}

class RecapObject :
	def __init__(self):
		self.date = time.strftime("%B %d, %Y")
		self.verse = Verse()
		self.quote = Quote()
		self.news = News()

# theoretical when refreshed in span of short time, when refresh after two hours first batch can be possibly seen again
class News: 
	def __init__(self,obj=None):
		urls = ["https://www.reddit.com/r/worldnews", "https://www.reddit.com/r/news"]
		self.headlines = []
		self.links = []
		self.show = True
		for link in urls:
			html = requests.get(link,headers=hdr)
			soup = BeautifulSoup(html.text, 'lxml')
			entries = soup.find_all('div','entry')
			if obj == None:
				self.nRead = []
				for i in range(0,3):
					self.headlines.append(entries[i].p.a.text)
					self.links.append(entries[i].p.a['href'])
			else :
				self.nRead = obj.nRead + obj.links
				index = count = 0
				while count < 3 and index < len(entries) :
					if entries[index].p.a['href'] not in self.nRead:
						self.headlines.append(entries[index].p.a.text)
						self.links.append(entries[index].p.a['href'])
						count += 1
					index +=1
	def display(self):
		print "-- IN THE NEWS --"
		for i in range(0,len(self.headlines)):
			print "[%d] %s" % (i+1,self.headlines[i])
	def newsRead(self,num):
		self.nRead.append(self.links[num-1])
		del self.headlines[num-1]
		del self.links[num-1]

class Verse:
	def __init__(self):
		bible_html = requests.get("http://www.biblestudytools.com/bible-verse-of-the-day/")
		soup = BeautifulSoup(bible_html.text, 'lxml')
		box = soup.find('p',{'class':'scripture'})
		# MAKE EACH VERSE DISPLAY SEPARATELY ON LINE SO IT DOESNT GET TOO LONG
		self.verse = " ".join(str(box.a.text).split())
		lines = box.find('span','verse').text
		self.text = " ".join(str(lines).split())
		self.show = True
	def display(self):
		print "[VERSE] %s - %s\n" % (self.text, self.verse)
	# def storeVerse(self):
	# 	#store in db

class Quote:
	def __init__(self):
		html = requests.get("http://www.brainyquote.com/quotes_of_the_day.html")
		soup = BeautifulSoup(html.text, 'lxml')
		quote_block = soup.find('div',{'class':'boxyPaddingBig'})
		self.quote = quote_block.find('span','bqQuoteLink').a.text
		self.author = quote_block.find('div','bq-aut').a.text
		self.show = True
	def display(self):
		print "[QUOTE] %s - %s\n" % (self.quote, self.author)
	def refreshQuote(self):
		html = requests.get("http://inspirationalshit.com/quotes", headers=hdr)
		soup = BeautifulSoup(html.text, 'lxml')
		quote_block = soup.find('blockquote')
		self.quote = quote_block.p.text
		self.author = quote_block.footer.cite.text
	# def storeQuote(self):
	# 	#store in db

# class Forecast:
# 	def __init__(self,day,date,high,low,cond):
# 		self.day = day
# 		self.date = date
# 		self.high = high
# 		self.low = low
# 		self.cond = cond

# class Weather:
# 	def __init__(self):
# 		self.forecasts = []
# 		html = requests.get("http://www.weather.com/weather/5day/l/95123:4:US", headers=hdr)
# 		soup = BeautifulSoup(html.text, 'lxml')
# 		weather_block = soup.find('div','weather-table day-table list height')
# 		print weather_block.find_all('div','ng-scope')
# 		# print weather_block

def loadRecapObject():
	# check for pickle close?
	try :	
		with open('/Users/sehun/User Scripts/rotd/recap_data.pkl', 'rb') as input:
			rd = pickle.load(input)
			if rd.date == time.strftime("%B %d, %Y"): 
				return rd
			else :
				return RecapObject()
	except IOError: 
		return RecapObject()
 
def storeRecapObject(rd_obj):
	with open('/Users/sehun/User Scripts/rotd/recap_data.pkl', 'wb') as output:
		pickle.dump(rd_obj, output, -1)
	output.close()
	
def main(argv):
	parser = argparse.ArgumentParser(description='Recap of the Day! #ROTD')
	parser.add_argument('-a','--remove-all', action='store_true', help='hides all attributes')
	parser.add_argument('-n','--news-remove', action='store_true', help='removes news from the recap data shown')
	parser.add_argument('-q','--quote-store', action='store_true', help='store quote into database')
	parser.add_argument('-f','--find-new-quote', action='store_true', help='finds new inspirational quote')
	parser.add_argument('-v','--verse-store', action='store_true', help='stores verse into database')
	parser.add_argument('-r','--reset', action='store_true', help='reset all attributes to show again')
	parser.add_argument('-s','--sync-current-news', action='store_true', help='fetches fresh news from reddit/r/news and reddit/r/worldnews')
	parser.add_argument('-o','--open-link', help='opens a new tab in browser with link to news article of provided choice')
	args = parser.parse_args()
	# Load object
	rd = loadRecapObject()
	if args.sync_current_news: 
		rd.news = News(rd.news)
	elif args.open_link :
		webbrowser.open_new_tab(rd.news.links[int(args.open_link)-1])
		rd.news.newsRead(int(args.open_link))
	else:
		if args.news_remove: 
			rd.news.show = not args.news_remove
		if args.remove_all: 
			rd.news.show = rd.verse.show = rd.quote.show = not args.remove_all
		if args.reset:
			rd.news.show = rd.verse.show = rd.quote.show = args.reset
		if args.find_new_quote: rd.quote.refreshQuote()
		for attr in [rd.verse, rd.quote, rd.news]:
			if attr.show : attr.display()
	storeRecapObject(rd)

if __name__ == '__main__' :
	main(sys.argv[1:])
	# Weather()
# DATABASE OPERATIONS
# db = MySQLdb.connect("localhost","db_user","db_password","pers_data")
# cursor = db.cursor()
# cursor.execute("SELECT * from quotes")
# try:
# 	quotes_row = cursor.fetchall()
# 	for row in quotes_row:
# 		print row[0]
# 		print row[1]
# except:
# 	print "Unable to fetch data from quotes"
# db.close()