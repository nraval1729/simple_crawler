import argparse
from Crawler import Crawler

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('seed', type=str)
	parser.add_argument('max_urls', type=int)

	args = parser.parse_args()

	crawler = Crawler(args.seed, args.max_urls)
	crawler.crawl()
	
	print "Finished crawling"

if __name__ == "__main__":
	main()
