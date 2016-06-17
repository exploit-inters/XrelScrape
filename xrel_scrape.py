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
                
def parse_titles(soup,cat):
    titles = []
    for tag in soup.findAll("a", { "class" : "sub_link"}):
        try:
            tag = str(tag)
            if 'title="' in tag:
                title = tag.split('title="')[1].split('"')[0]
            else:
                title = tag.split('_title')[1]
                title = title.split('">')[1].split('</span>')[0]
                titles.append(title)
        except:
            pass
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
        soup = BeautifulSoup(str(html), "html.parser")
        return int(soup.findAll("a", { "class" : "page"})[-1].text)
    except:
        return 1
    

def get_html(page,cat,date):
    url = "https://www.xrel.to/"+ get_qer(cat) +".html?archive="+date+"&page="+str(page)
    ua = UserAgent().random
    req = urllib2.Request(url, headers={'User-Agent': ua,'Accept':'*/*'})
    html = urllib2.urlopen(req).read()
    soup = BeautifulSoup(html, "html.parser")
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

def loader(cat,date):
    global q
    q = gevent.queue.JoinableQueue()
    now = datetime.datetime.now()
    if date == 'now':
        date = str(now.strftime("%Y-%m-%d %H:%M")[:-9])
    pcount = parse_nextpage(cat,date)
    global bar
    bar = Bar('Processing page', max=pcount-1)
    for i in range(1,pcount):
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
        print "Saving",args['output'],'.'
        with open(o, "wb") as the_file:
            csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
            writer = csv.writer(the_file, dialect="custom")
            writer.writerow((['release','size(mb)','date']))
            for tup in names:
                writer.writerow(tup)
    else:
        for s in names:
            print s




def main(args=None):
    print "Xrel Sraper 1.0"
    parser = argparse.ArgumentParser(description='Xrel.to Scraper 1.0')
    parser.add_argument('-c','--category', help='''movies top-movies console games apps tv
    english hotstuff xxx games-p2p apps-p2p console-p2p tv-p2p apps-p2p movies-p2p
    ''', required=False,type=str,default="apps-p2p")
    parser.add_argument('-d','--date', help="2016-06", required=False,type=str,default="now")
    parser.add_argument('-t','--threads', help='', required=False,type=int,default="25")
    parser.add_argument('-o','--output', help='example.csv', required=False,type=str)
    args = vars(parser.parse_args())
    gevent.monkey.patch_all()
    cat = args['category']
    date = args['date']
    workers = args['threads']
    gevent.spawn(loader(cat,date)).join()
    asynchronous(workers)
    print "\nFound:",len(names),"releases.\n"
    save(args['output'])
    print "Done."
    time.sleep(10)


if __name__ == "__main__":
    main()
        



