# XrelScrape
Xrel.to Scraper

Scrapes given category for given month and returns release names, file size (in Megabyte) and date of release.

Gevent is used to implement concurrency.

Example usage: xrel_scrape -c apps -daterange 2016-01,2016-3 -o apps.csv -t 20

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
  -ep ERRORPAGES, --errorpages ERRORPAGES
                        Print pages with an error.
                        
                        
                        
Note: There is a random blocking of requests in place which results in some pages not beeing scraped.
You can see which pages were not scraped with the -ep switch.
                        
                
