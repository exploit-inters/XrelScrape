#!/usr/bin/python
import argparse
import gevent
from gevent.queue import *
import gevent.monkey
import urllib2
from bs4 import BeautifulSoup #pip install BeautifulSoup4
from timeit import default_timer as timer
import datetime
import random
import time
from fake_useragent import UserAgent #pip install fake-useragent
from progress.bar import Bar #pip install progress
import csv
import sys
import calendar
import datetime

def months_iter(start_month, start_year, end_month, end_year):
    #http://stackoverflow.com/a/5735013
    start_date = datetime.date(start_year, start_month, 1)
    end_date = datetime.date(end_year, end_month, 1)
    date = start_date
    while date <= end_date:
        yield (date.month, date.year)
        days_in_month = calendar.monthrange(date.year, date.month)[1]
        date += datetime.timedelta(days_in_month)

def months(start_month, start_year, end_month, end_year):
    #http://stackoverflow.com/a/5735013
    return tuple(d for d in months_iter(start_month, start_year, end_month, end_year))

def parse_titles(soup,cat):
    titles = []
    for div in soup.findAll("div", { "class" : "release_title"}):
        if '...' in div.text:
            s = BeautifulSoup(str(div), "lxml")
            a = s.span.attrs
            titles.append(str(a['title']))
        else:
            a = div.text.strip()
            titles.append(str(a.split('  ')[1]))
    return titles

def parse_sizes(soup):
    sizes = []
    for tag in soup.findAll("span", { "class" : "sub"}):
        try:
            if 'MB' in str(tag):
                size = str(tag).split('>')[1].split('<')[0].split(' ')[0]
                sizes.append(str(size))
        except:
            pass
    return sizes

def parse_date(soup):
    dors = []
    for tag in soup.findAll("div", { "class" : "release_date"}):
        try:
            dor = str(tag.text.strip())
            dor = dor[:8]+'-'+dor[8:-4]
            dors.append(dor)
        except:
            pass
    return dors

def get_qer(cat):
        quer = {'movies':'movies-release-list','top-movies':'movie-topmovie-release-list',
            'console':'console-release-list','games':'game-windows-release-list',
            'apps-win':'apps-release-list','apps':'apps-release-list','tv':'tv-release-list',
            'english':'english-release-list','hotstuff':'hotstuff-release-list',
            'xxx':'xxx-xxx-release-list','movies-p2p':'p2p/15-movie/releases',
            'games-p2p':'p2p/9-games/releases','apps-p2p':'p2p/12-software',
            'console-p2p':'p2p/10-console/releases','tv-p2p':'p2p/16-tv/releases',
            'apps-p2p':'p2p/12-software/releases'}
        return str(quer[cat])

def parse_nextpage(cat,date):
    try:
        soup = get_html(2,cat,date)
        html = soup.find("div", { "class" : "pages clearfix"})
        soup = BeautifulSoup(str(html), "lxml")
        page = int(soup.findAll("a", { "class" : "page"})[-1].text)
        if page == 1:
            return 2
        else:
            return page
    except:
        return 2

def get_html(page,cat,date):
    url = "https://www.xrel.to/"+ get_qer(cat) +".html?archive="+date+"&page="+str(page)
    ua = UserAgent().random
    req = urllib2.Request(url, headers={'User-Agent': ua,'Accept':'*/*'})
    html = urllib2.urlopen(req).read()
    soup = BeautifulSoup(html, "lxml")
    return soup

def scrape(page,cat,date):
    soup = get_html(page,cat,date)
    rl_name = parse_titles(soup,cat)
    mb = parse_sizes(soup)
    date = parse_date(soup)
    return zip(rl_name, mb,date)

def worker():
    global names
    names = []
    while not q.empty():
        t = q.get()
        try:
            r = scrape(t[0],t[1],t[2])
            names.extend(r)
        except:
            q.put(t, timeout=3)
        finally:
            gevent.sleep(random.uniform(0.011,0.025))
            bar.next()

def loader(cat,date,date_iter):
    global q
    global bar
    q = gevent.queue.JoinableQueue()
    if date == 'now':
        now = datetime.datetime.now()
        date = str(now.strftime("%Y-%m-%d %H:%M")[:-9])

    date_range_c = []
    if date_iter != None:
        try:
            date_iter = date_iter.split(',')
            date_iter = date_iter[0].split('-')[::-1],date_iter[1].split('-')[::-1]
            date_range = months(int(date_iter[0][0]), int(date_iter[0][1]), int(date_iter[1][0]), int(date_iter[1][1]))
            date_range[0]
            for i in date_range:
                 date_range_c.append(str(i[1])+'-'+str(i[0]))

            pcount_range = []
            pcount_range_sum = 0
            for mo in date_range_c:
                e = parse_nextpage(cat,mo)
                pcount_range.append(e)
                pcount_range_sum = pcount_range_sum + e

            bar = Bar('Processing page', max=pcount_range_sum)
        except:
            print "Format Error: Range has to be in format 2014-05,2016-05!"
            sys.exit()

    if len(date_range_c)>0:
        for date in date_range_c:
            for j in pcount_range:
                for i in range(1,j+1):
                    q.put((i,cat,date), timeout=6)
    else:
        pcount = parse_nextpage(cat,date)
        bar = Bar('Processing page', max=pcount)
        for i in range(1,pcount+1):
            q.put((i,cat,date), timeout=6)

def asynchronous(workers):
    threads = []
    for i in range(workers):
        threads.append(gevent.spawn(worker))
    start = timer()
    gevent.joinall(threads,raise_error=True)
    bar.finish()
    end = timer()
    print ""
    print "Time passed: " + str(end - start)[:6]

def save(o):
    if o != None:
        print "Saving:",o,
        with open(o, "wb") as the_file:
            csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
            writer = csv.writer(the_file, dialect="custom")
            writer.writerow((['release','size(mb)','date']))
            for tup in names:
                writer.writerow(tup)
    else:
        print "Release,Size(MB),Date"
        for s in names:
            print s

def main(args=None):
    asci = '''
    __  __        _ ___
    \ \/ /_ _ ___| / __| __ _ _ __ _ _ __  ___
     >  <| '_/ -_) \__ \/ _| '_/ _` | '_ \/ -_)
    /_/\_\_| \___|_|___/\__|_| \__,_| .__/\___|
         by SUP3RIA                 |_|  v1.0.1
    '''
    print asci+'\n'
    parser = argparse.ArgumentParser(description='Xrel.to Scraper 1.0')
    parser.add_argument('-c','--category', help='''movies top-movies console games apps tv
    english hotstuff xxx games-p2p apps-p2p console-p2p tv-p2p apps-p2p movies-p2p
    ''', required=False,type=str,default="apps")
    parser.add_argument('-d','--date', help="2016-06", required=False,type=str,default="now")
    parser.add_argument('-dr','--daterange', help='2014-05,2016-05', required=False,type=str)
    parser.add_argument('-t','--threads', help='', required=False,type=int,default="12")
    parser.add_argument('-o','--output', help='example.csv', required=False,type=str)

    args = vars(parser.parse_args())
    gevent.monkey.patch_all()
    cat = args['category']
    date = args['date']
    date_iter = args['daterange']
    workers = args['threads']
    gevent.spawn(loader(cat,date,date_iter)).join()
    asynchronous(workers)
    print "\nFound:",len(names),"releases.\n"
    save(args['output'])
    print "\nDone."

if __name__ == "__main__":
    main()
