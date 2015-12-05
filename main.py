import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import html2text
import csv # pro exportovani do CSV
# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

br.addheaders = [('User-agent', 'Chrome')]

# The site we will navigate into, handling it's session
br.open('https://login.heureka.cz/login')

# View available forms
#for f in br.forms():
#    print f

# Select the second (index one) form (the first form is a search query box)
br.select_form(nr=0)

# User credentials
br.form['mail'] = 'valiska@sportmall.cz'
br.form['password'] = 'heurech15'

# Login
br.submit()

from lxml import html
import requests

shop = 'Kolonial.cz'
date = '2015-09-29'
page = br.open('http://sluzby.heureka.cz/obchody/statistiky/?from=2015-09-29&to=2015-10-29&shop=53090&cat=-4').read()
tree = html.fromstring(page)

soup1 = BeautifulSoup(page)
tabulka = soup1('table',{'class':'shop-list roi'})

rows = BeautifulSoup(str(tabulka)).findChildren(['tr'])
