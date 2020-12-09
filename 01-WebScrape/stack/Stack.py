import re
import time
import requests

from bs4 import BeautifulSoup



class stack_scrape(object):    
  
	def __init__(self):
		pass


	def extract_data_from_url(self, url):
		'''
		Returns the scraped data from the target URL in raw format (HTML), which can be stackoverflow or stackexchange
		
		
		Paramaters
		----------
		url: url of the website to be scraped (parameter passed by scrape_data function) 
		
		Returns
		-------
		a JSON with the raw format (HTML) of all the page (BeautifulSoup object)
		'''

		# server request
		response = requests.get(url)
		# Read the request, as a HTML text
		html = response.text
		# String -> Soup (special data structure of information)
		soup = BeautifulSoup(html, 'html.parser')
		# Extracts the desired information from the website and passes it on to json
		data = stack_scrape.parse_tagged_page(self, soup)
		return data



	def multiply_views(self, text):
		'''
		checks for the existence of an order of magnitude (e.g. 10k), converts this string to a value by multiplying\n by the respective order of magnitude value
		
		
		Paramaters
		----------
		text: given to be treated, parameter passed by the clean_scraped_data function
		
		Returns
		-------
		returns an integer
		'''
			
		# multiplier ratio by order of magnitude
		pattern = {
					'k': 1000,
					'm': 1000000
				}
		
		# multiplication of the value by the order of magnitude
		try: 
			mult = int(re.search('(\d+)', text).group(1)) * pattern[re.search('([A-Za-z]+)', text).group(1)]
			
		# exception for smaller data which is the smallest order of magnitude
		except AttributeError:
			mult = int(re.search('(\d+)', text).group(1))

		return mult



	def clean_scraped_data(self, text , keyname=None):
		'''
		performs data transformations as trim of the data if necessary and calls another function to handle values
		
		
		Paramaters
		----------
		text: given to be treated, parameter passed by the parse_tagged_page function
		keyname: refers to which encapsulation function should be performed by means of a key-value
				- default=None
		
		Returns
		-------
		returns the data with the proper transformation
		'''
			
		# encapsulated treatments by means of a key
		transforms = {
			'votes': text.replace('\nvotes', ''),
			'answer': text.replace('answer', '').strip('s'),
			'views': text.replace('views', '')
		}
		
		# application of the treatment
		if keyname in transforms.keys():
			
			# application of excision treatment
			if keyname == 'views':
				
				# transformation of the data into an integer and multiplies it by the order of magnitude
				trasnf = stack_scrape.multiply_views(self, transforms[keyname])
				return trasnf
			
			return transforms[keyname]
		
		# data that do not need treatment
		else:
			return text

		
		

	def get_id(self, q):
		'''
		returns the clean question id on page
		
		
		Paramaters
		----------
		q: cleaning target, this parameter is passed by parse_tagged_page function 
		
		Returns
		-------
		string with the clean question id
		'''
		
		# cleaning pattern
		pattern = 'href="/questions/([^"]+)[\/]'
		
		# applies the established pattern to extract the id
		q_id = re.search(pattern,q).group(1)
		
		return q_id


	
	

	def parse_tagged_page(self, soup):
		'''
		Returns the scraped data from the target URL, which can be stackoverflow or stackexchange
		
		
		Paramaters
		----------
		soup: a JSON with the raw format (HTML) of all the page (BeautifulSoup object), this parameter is passed by extract_data_from_url function 
		
		Returns
		-------
		a JSON with the 'Question', 'Number of Votes', 'question-related tags', 'number of responses' and 'number of views' data\n\t\t from the records of one page
		'''
		
		# css target class
		question_summaries = soup.select('.question-summary')
		# list of names to be assigned to data
		key_names = ['question', 'votes', 'tags', 'answer', 'views']
		# css target class subclasses 
		classes_needed = ['.question-hyperlink', '.vote', '.tags', '.status', '.views']
		
		datas = []
		# loop in each data extracted through the target css class
		for q_el in question_summaries:
			question_data = {}
			
			# loop in each enumerate subclass listed above
			for i, _class in enumerate(classes_needed):
				# obtain the value of each subclass
				sub_el = q_el.select(_class)[0]
				# obtains the value of each subclass to generate the dictionary key 
				keyname = key_names[i]
				# attach the given treaty with its respective key to the dictionary
				question_data[keyname] = stack_scrape.clean_scraped_data(self, sub_el.text.strip(), keyname=keyname)
				
				# subclass that receives a treatment of exception to the others
				if _class == '.question-hyperlink':
					# get the id of each question
					question_data['id'] = stack_scrape.get_id(self, str(sub_el))
					
			# attach the complete dictionary of each question to the empty list created	
			datas.append(question_data)

		return datas

	
	


	def scrape_data(self, base_url, tag, query_filter, max_pages, pagesize):
		'''
		Itera on all selected pages by rotating the function to extract the data from each page and gather it in a json
		
		Paramaters
		----------
		base_url: url path to all question filter by a tag
					- stackexchange: https://stats.stackexchange.com/questions/tagged/
					- stackoverflow: https://stackoverflow.com/questions/tagged/
					
		tag: tag to be filtered (e.g.: 'python', 'r', 'javascript', ...)
		
		query_filter: filter to perform a query ('Newest', 'Active', 'Bounties', 'Unanswered', 'Frequent', Votes')
		
		max_pages: the maximum number of pages to be scraped
		
		pagesize: the number of records per page (the maximum number is 50)
		
		
		Returns
		-------
		a JSON with the 'Question', 'Number of Votes', 'question-related tags', 'number of responses' and 'number of views' data\n\t\t from the records of all selected pages
		'''
		
		
		datas = list()
		# loop on each page of the given range
		for p in range(max_pages):
			# adjustment of the iteration variable
			page_num = p + 1
			# target page url formation
			url = f'{base_url}{tag}?tab={query_filter}&page={page_num}&pagesize={pagesize}'
			# url data extraction 
			datas += stack_scrape.extract_data_from_url(self, url)
			# time control
			time.sleep(0.5)
		return datas