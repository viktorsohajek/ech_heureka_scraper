# -*- coding: utf-8 -*-

import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import html2text
import csv # pro exportovani do CSV

# date input
from datetime import date, timedelta
yesterday = date.today() - timedelta(1)
date = yesterday.strftime('%Y-%m-%d')

#list shopu
dict={}
dict['Heureka.cz'] = {}
dict['Zbozi.cz'] = {}
dict['Heureka.cz']['Login_1'] = {'Login': 'valiska@sportmall.cz',
                     'Password': 'heurech15',
                     'Url_login': 'https://login.heureka.cz/login',
                     'Shop': ['Sporty.cz','Snowboards.cz','Kolonial.cz','Prodeti.cz'],
                     'Url_stats': ['http://sluzby.heureka.cz/obchody/statistiky/?shop=5709&from='+date+'&to='+date+'&cat=-4','http://sluzby.heureka.cz/obchody/statistiky/?shop=1786&from='+date+'&to='+date+'&cat=-4','http://sluzby.heureka.cz/obchody/statistiky/?shop=53090&from='+date+'&to='+date+'&cat=-4','http://sluzby.heureka.cz/obchody/statistiky/?shop=45555&from='+date+'&to='+date+'&cat=-4'],
                     'Storage_name': ['heureka_sm.csv','heureka_snb.csv','heureka_kn.csv','heureka_pd.csv']}

dict['Heureka.cz']['Login_2'] = {'Login': 'heureka@bigbrands.cz',
                     'Password': 'ecommerceheureka',
                     'Url_login': 'https://login.heureka.cz/login',
                     'Shop': ['BigBrands.cz'],
                     'Url_stats': ['http://sluzby.heureka.cz/obchody/statistiky/?from='+date+'&to='+date+'&shop=42893&cat=-4'],
                     'Storage_name': ['heureka_bb.csv'] }

dict['Heureka.cz']['Login_3'] = {'Login': 'info@limal.cz',
                     'Password': 'heureka123456',
                     'Url_login': 'https://login.heureka.cz/login',
                     'Shop': ['Rozbaleno.cz'],
                     'Url_stats': ['http://sluzby.heureka.cz/obchody/statistiky/?from='+date+'&to='+date+'&shop=6590&cat=-4'],
                     'Storage_name': ['heureka_ro.csv']}


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


        keys = ['name', 'visits', 'cpc', 'costs', 'currency','shop','date']
        #csv.register_dialect('singlequote', quotechar="'", quoting=csv.QUOTE_ALL)
        #csv.register_dialect('escaped', escapechar='\\', doublequote=False, quoting=csv.QUOTE_NONE)

        with open('/data/out/tables/'+dict['Heureka.cz'][login]['Storage_name'][index], 'wb') as output_file:
            dict_writer = csv.DictWriter(output_file, keys, quoting=csv.QUOTE_NONNUMERIC)
            dict_writer.writeheader()
            dict_writer.writerows(L)
