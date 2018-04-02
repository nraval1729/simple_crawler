**Dependencies**

- Python 2.7
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests](http://docs.python-requests.org/en/master/)

**Running**
- `git clone https://github.com/nraval1729/simple_crawler.git`
- `python crawler_cli.py <seed_url> <max_number_of_urls>`, where `seed_url` is the url from which you want to start crawling, and `max_number_of_urls` is the maximum number of urls to crawl. The crawler will terminate after roughly hitting this number.

**Design decisions**

 - Stateless in-memory implementation.
 - Multithreaded setup.
 - Exponential backoff strategy with retries to account for unexpected network errors.
 - Uses a reentrant lock so that the worker threads can collaborate on the dictionary object.
 - Error checking for malformed urls.
 - Print the urls to the console as and when the crawler finishes crawling them.
 - Accept command line arguments for seed url and max number of urls to crawl.

