from Queue import Queue, Empty
import threading
from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout
import sys

class Crawler:
	def __init__(self, seed_url, max_urls):
		self.SEED_URL = seed_url
		self.MAX_URLS = max_urls
		self.NUM_THREADS = 5
		self.MAX_URLS_PER_WORKER = self.MAX_URLS/self.NUM_THREADS
		self.LOCK = threading.RLock()
		self.workers = []

		# Create a requests session that supports retry with exponential
		# backing for http codes 500, 502, 503, 504
		self.session = requests.Session()
		retries = Retry(total=5,
	                backoff_factor=0.2,
	                status_forcelist=[ 500, 502, 503, 504 ])

		# Apply the custom adapter for urls with these two prefixes
		self.session.mount('http://', HTTPAdapter(max_retries=retries))
		self.session.mount('https://', HTTPAdapter(max_retries=retries))

		# Check to see if the seed is valid. If not,
		# terminate the process with error message
		self.validate_seed_url()

		self.seen = {}
		self.to_be_parsed = Queue()
		self.to_be_parsed.put(seed_url)

	def crawl(self):
		# Kickstart the workers
		for i in range(self.NUM_THREADS):
			worker = threading.Thread(target=self.worker_operation)
			worker.start()
			self.workers.append(worker)

		# Wait for all workers to finish
		for worker in self.workers:
			worker.join()

	def worker_operation(self):
		my_seen_count = 0
		while True:
			try:
				curr_url = self.to_be_parsed.get_nowait()

				self.LOCK.acquire()
				try:
					# Now we've "seen" the curr_url
					self.seen[curr_url] = True
					my_seen_count += 1
				finally:
					self.LOCK.release()

				print "Crawled: ", curr_url

				for outgoing_url in self.get_all_outgoing_urls_from(curr_url):
					if my_seen_count <= self.MAX_URLS_PER_WORKER:
						if outgoing_url not in self.seen:
							self.to_be_parsed.put(outgoing_url)
					else:
						return

			except Empty:
				pass

	def get_all_outgoing_urls_from(self, url):
		try:
			content = self.session.get(url, timeout=5)
			soup = BeautifulSoup(content.text, "lxml")
			outgoing_urls = []

			for a_tag in soup.find_all('a', href=True):
				url = a_tag['href']

				# Only absolute urls
				if url.startswith('http://') or url.startswith('https://'):
					outgoing_urls.append(url)

			return outgoing_urls

		# If we hit a Timeout,
		# we move on, but place the url back in the
		# to_be_parsed Queue for other threads to 
		# potentially try parsing
		except Timeout:
			self.to_be_parsed.put_nowait(url)
		except:
			return []

	def validate_seed_url(self):
		print "Validating seed url..."
		try:
			r = self.session.get(self.SEED_URL, timeout=10)
			print "Seed url is valid."
		except ConnectionError:
			print "Seed url: ", self.SEED_URL, " is non-existent. Please enter a valid url."
			print "Exiting..."
			sys.exit(1)
		except Exception as e:
			print str(e)
			sys.exit(1)
