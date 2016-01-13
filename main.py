# -*- coding: utf-8 -*-

import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import html2text
import csv # pro exportovani do CSV
from keboola import docker
import datetime
from datetime import date, timedelta # date input

# initialize KBC configuration 
cfg = docker.Config('/data/')
# validate application parameters
parameters = cfg.getParameters()


# date format checker
def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

scrape_dates={}

#date preset from input parameters
if parameters.get('Date_preset')=='Yesterday':
	yesterday = date.today() - timedelta(1)
	scrape_dates[0] = yesterday.strftime('%Y-%m-%d')
else:
	validate(parameters.get('Date_from'))
	validate(parameters.get('Date_to'))
	d1=datetime.datetime.strptime(parameters.get('Date_from'),'%Y-%m-%d')
	d2=datetime.datetime.strptime(parameters.get('Date_to'),'%Y-%m-%d')
	delta = d2 - d1
	for i in range(delta.days+1):
		scrape_dates[i]=(d1+timedelta(i)).strftime('%Y-%m-%d')


for i in range(len(scrape_dates)):
	scrape_date=scrape_dates[i]
	#list shopu
	dict={}
	dict['Heureka.cz'] = {}
	dict['Heureka.cz']['Login_1'] = {'Login': parameters.get('Login_1').get('Login'),
	                     'Password': parameters.get('Login_1').get('Password'),
	                     'Url_login': 'https://login.heureka.cz/login',
	                     'Shop': ['Prodeti.cz','Sporty.cz','Snowboards.cz','Kolonial.cz'],
	                     'Url_stats': ['http://sluzby.heureka.cz/obchody/statistiky/?shop=45555&from='+scrape_date+'&to='+scrape_date+'&cat=-4','http://sluzby.heureka.cz/obchody/statistiky/?shop=5709&from='+scrape_date+'&to='+scrape_date+'&cat=-4','http://sluzby.heureka.cz/obchody/statistiky/?shop=1786&from='+scrape_date+'&to='+scrape_date+'&cat=-4','http://sluzby.heureka.cz/obchody/statistiky/?shop=53090&from='+scrape_date+'&to='+scrape_date+'&cat=-4'],
	                     'Storage_name': ['heureka_pd.csv','heureka_sm.csv','heureka_snb.csv','heureka_kn.csv']}

	dict['Heureka.cz']['Login_2'] = {'Login': parameters.get('Login_2').get('Login'),
	                     'Password': parameters.get('Login_2').get('Password'),
	                     'Url_login': 'https://login.heureka.cz/login',
	                     'Shop': ['BigBrands.cz'],
	                     'Url_stats': ['http://sluzby.heureka.cz/obchody/statistiky/?from='+scrape_date+'&to='+scrape_date+'&shop=42893&cat=-4'],
	                     'Storage_name': ['heureka_bb.csv'] }

	dict['Heureka.cz']['Login_3'] = {'Login': parameters.get('Login_3').get('Login'),
	                     'Password': parameters.get('Login_3').get('Password'),
	                     'Url_login': 'https://login.heureka.cz/login',
	                     'Shop': ['Rozbaleno.cz'],
	                     'Url_stats': ['http://sluzby.heureka.cz/obchody/statistiky/?from='+scrape_date+'&to='+scrape_date+'&shop=6590&cat=-4'],
	                     'Storage_name': ['heureka_ro.csv']}

	# Cisti stringy obsahujici cislo a menu od mezer a rozpada je na dva stringy : hodnotu a menu
	def sanitizeStrings(text) :
	    textSplitted = text.string.rsplit('&',1)
	    firstResultTemp  = textSplitted[0].replace('&nbsp;','') #pro pripad, ze je cislo vetsi nez 999 a cislo je ve formatu 'X XXX'
	    firstResult = float(firstResultTemp.replace(',','.'))
	    secondResult = textSplitted[1]
	    return firstResult, secondResult

	for login in dict['Heureka.cz'].keys():
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
	    br.form['mail'] = dict['Heureka.cz'][login]['Login']
	    br.form['password'] = dict['Heureka.cz'][login]['Password']

	    # Login
	    br.submit()

	    from lxml import html
	    import requests

	    no_of_shops=len(dict['Heureka.cz'][login]['Shop'])

	    for index in range(0,no_of_shops):
	        shop = dict['Heureka.cz'][login]['Shop'][index]
	        page = br.open(dict['Heureka.cz'][login]['Url_stats'][index]).read()
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
	                temp = sanitizeStrings(cells[3])
	                costs = temp[0]
	                currency = temp[1]
	                if currency == u'nbsp;Kč' :
	                    currency = 'CZK'
	                    #doplnit eura
	                # cpc cisteni a uprava
	                #print(costs)
	                #print(currency)
	                temp = sanitizeStrings(cells[2])
	                cpc = temp[0]

	                # visits cisteni a uprava
	                visits_temp = cells[1].string.replace('&nbsp;','') #pro pripad, ze je cislo vetsi nez 999 a cislo je ve formatu 'X XXX'
			visits = float(visits_temp)

	                # name cisteni a uprava
	                name = cells[0].string
	                if name == None :
	                    name = 'Heureka.cz'

	                prvekL = {'shop':shop,
	                        'date':scrape_date,
	                        'name':name,
	                        'visits':visits,
	                        'cpc':cpc,
	                        'costs':costs,
	                        'currency':currency}
	                L.append(prvekL)
	            #for cell in cells:
	            #    value = cell.string
	            #    prvekL.append(value)


	        keys = ['name', 'visits', 'cpc', 'costs', 'currency','shop','date']
	        #csv.register_dialect('singlequote', quotechar="'", quoting=csv.QUOTE_ALL)
	        #csv.register_dialect('escaped', escapechar='\\', doublequote=False, quoting=csv.QUOTE_NONE)

	        with open('/data/out/tables/'+dict['Heureka.cz'][login]['Storage_name'][index], 'ab') as output_file:
	            dict_writer = csv.DictWriter(output_file, keys, quoting=csv.QUOTE_NONNUMERIC)
	            dict_writer.writeheader()
	            dict_writer.writerows(L)
