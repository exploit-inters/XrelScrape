# XrelScrape
Xrel.to Scraper

Scrapes given category for given month and returns release names, file size (in Megabyte) and date of release.

Gevent is used to implement concurrency.


    __  __        _ ___
    \ \/ /_ _ ___| / __| __ _ _ __ _ _ __  ___
     >  <| '_/ -_) \__ \/ _| '_/ _` | '_ \/ -_)
    /_/\_\_| \___|_|___/\__|_| \__,_| .__/\___|
         by SUP3RIA                 |_|  v1.0.1


usage: xrel_scrape.py [-h] [-c CATEGORY] [-d DATE] [-dr DATERANGE]
                      [-t THREADS] [-o OUTPUT]

Xrel.to Scraper 1.0

optional arguments:
  -h, --help            show this help message and exit
  -c CATEGORY, --category CATEGORY
                        movies top-movies console games apps tv english
                        hotstuff xxx games-p2p apps-p2p console-p2p tv-p2p
                        apps-p2p movies-p2p
  -d DATE, --date DATE  2016-06
  -dr DATERANGE, --daterange DATERANGE
                        2014-05,2016-05
  -t THREADS, --threads THREADS
  -o OUTPUT, --output OUTPUT
                        example.csv
