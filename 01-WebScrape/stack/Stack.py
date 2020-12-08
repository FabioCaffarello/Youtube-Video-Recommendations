import re
import time
import requests

from bs4 import BeautifulSoup



class stack_scrape(object):    
  
	def __init__(self):
		pass


	def extract_data_from_url(self, url):
		
		response = requests.get(url)
		html = response.text
		soup = BeautifulSoup(html, 'html.parser')
		data = stack_scrape.parse_tagged_page(self, soup)
		return data



	def multiply_views(self, text):
		text.replace('views', '').strip()
		pattern = {
					'k': 1000,
					'm': 1000000
				}
		try: 
			mult = int(re.search('(\d+)', text).group(1)) * pattern[re.search('([A-Za-z]+)', text).group(1)]
		except AttributeError:
			mult = int(re.search('(\d+)', text).group(1))

		return mult



	def clean_scraped_data(self, text , keyname=None):
		transforms = {
			'votes': text.replace('\nvotes', ''),
			'answer': text.replace('answers', ''),
			'views': text.replace('views', '')
		}
		if keyname in transforms.keys():

			if keyname == 'views':
				trasnf = stack_scrape.multiply_views(self, transforms[keyname])
				return trasnf
			
			return transforms[keyname]
		else:
			return text


	def get_id(self, q):

		pattern = 'href="/questions/([^"]+)[\/]'
		q_id = re.search(pattern,q).group(1)
		return q_id



	def parse_tagged_page(self, soup):
		question_summaries = soup.select('.question-summary')
		key_names = ['question', 'votes', 'tags', 'answer', 'views']
		classes_needed = ['.question-hyperlink', '.vote', '.tags', '.status', '.views']
		datas = []
		for q_el in question_summaries:
			question_data = {}
			for i, _class in enumerate(classes_needed):
				sub_el = q_el.select(_class)[0]
				keyname = key_names[i]
				question_data[keyname] = stack_scrape.clean_scraped_data(self, sub_el.text.strip(), keyname=keyname)
				if _class == '.question-hyperlink':
					question_data['id'] = stack_scrape.get_id(self, str(sub_el))
			datas.append(question_data)

		return datas



	def scrape_data(self, base_url, tag, query_filter, max_pages, pagesize):
		datas = list()
		for p in range(max_pages):
			page_num = p + 1
			url = f'{base_url}{tag}?tab={query_filter}&page={page_num}&pagesize={pagesize}'
			datas += stack_scrape.extract_data_from_url(self, url)
			time.sleep(0.5)
		return datas