# -*- coding: utf-8 -*-

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

L = [] # deklarujeme prazdny list s vysledky
for row in rows:
    cells = row.findChildren('td')
    cells = cells[0:4] #chceme jen jmeno vyhledavace a prvni tri hodnty
    if len(cells) >= 4 :
        # costs cisteni a uprava
        costsWithCurrency = cells[3].string.split('&')
        costs = float(costsWithCurrency[0].replace(',','.'))
        currency = costsWithCurrency[1]
        if currency == u'nbsp;Kč' :
            currency = 'CZK'
            #doplnit eura
        # cpc cisteni a uprava
        cpcWithCurrency = cells[2].string.split('&')
        cpc = float(cpcWithCurrency[0].replace(',','.'))
        # visits cisteni a uprava
        visits = float(cells[1].string)
        # name cisteni a uprava
        name = cells[0].string
        if name == None :
            name = 'Heureka.cz'

        prvekL = {'shop':shop,
                  'date':date,
                  'name':name,
                  'visits':visits,
                  'cpc':cpc,
                  'costs':costs,
                  'currency':currency}
        L.append(prvekL)
    #for cell in cells:
    #    value = cell.string
    #    prvekL.append(value)

#print L

keys = ['name', 'visits', 'cpc', 'costs', 'currency','shop','date']
#csv.register_dialect('singlequote', quotechar="'", quoting=csv.QUOTE_ALL)
#csv.register_dialect('escaped', escapechar='\\', doublequote=False, quoting=csv.QUOTE_NONE)

with open('result.csv', 'wb') as output_file:
    dict_writer = csv.DictWriter(output_file, keys, quoting=csv.QUOTE_NONNUMERIC)
    dict_writer.writeheader()
    dict_writer.writerows(L)
