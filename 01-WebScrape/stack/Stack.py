import re
import time
import json
import requests
import joblib as jp
import pandas as pd

from bs4 import BeautifulSoup



class stackScrape(object):    
  
	def __init__(self):
		pass


	def extractDataFromUrl(self, url):
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
		data = stackScrape.parseTaggedPage(self, soup)
		return data



	def multiplyViews(self, text):
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



	def cleanScrapedData(self, text , keyname=None):
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
			'votes': text.replace('\nvote', '').strip('s'),
			'answer': text.replace('answer', '').strip('s'),
			'views': text.replace('views', '')
		}
		
		# application of the treatment
		if keyname in transforms.keys():
			
			# application of excision treatment
			if keyname == 'views':
				
				# transformation of the data into an integer and multiplies it by the order of magnitude
				trasnf = stackScrape.multiplyViews(self, transforms[keyname])
				return trasnf
			
			return transforms[keyname]
		
		# data that do not need treatment
		else:
			return text

		
		

	def getId(self, q):
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


	
	

	def parseTaggedPage(self, soup):
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
		questionSummaries = soup.select('.question-summary')
		# list of names to be assigned to data
		keyNames = ['question', 'votes', 'tags', 'answer', 'views']
		# css target class subclasses 
		classesNeeded = ['.question-hyperlink', '.vote', '.tags', '.status', '.views']
		
		datas = []
		# loop in each data extracted through the target css class
		for q_el in questionSummaries:
			questionData = {}
			
			# loop in each enumerate subclass listed above
			for i, _class in enumerate(classesNeeded):
				# obtain the value of each subclass
				sub_el = q_el.select(_class)[0]
				# obtains the value of each subclass to generate the dictionary key 
				keyname = keyNames[i]
				# attach the given treaty with its respective key to the dictionary
				questionData[keyname] = stackScrape.cleanScrapedData(self, sub_el.text.strip(), keyname=keyname)
				
				# subclass that receives a treatment of exception to the others
				if _class == '.question-hyperlink':
					# get the id of each question
					questionData['id'] = stackScrape.getId(self, str(sub_el))
					
			# attach the complete dictionary of each question to the empty list created	
			datas.append(questionData)

		return datas




	def scrapeData(self, base_url, tag, query_filter, max_pages, pagesize):
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
		a DataFrame with the 'Question', 'Number of Votes', 'question-related tags', 'number of responses' and 'number of views' data\n\t\t from the records of all selected pages
		'''


		datas = list()
		# loop on each page of the given range
		for p in range(max_pages):
			# adjustment of the iteration variable
			page_num = p + 1
			# target page url formation
			url = f'{base_url}{tag}?tab={query_filter}&page={page_num}&pagesize={pagesize}'
			# url data extraction 
			datas += stackScrape.extractDataFromUrl(self, url)
			# time control
			time.sleep(0.5)
		
		# DataFrame
		dfStack = pd.DataFrame(datas, columns=datas[0].keys())
		# DataFrame convert dtypes (int)
		dfStack['votes'] = dfStack['votes'].astype(int)
		dfStack['answer'] = dfStack['answer'].astype(int)
		dfStack['views'] = dfStack['views'].astype(int)
		
		return dfStack
	
	
	
	
	def TagsStack(self, base_url, tag, query_filter, max_pages, pagesize):
		'''
		returns a dataframe with the top 15 tags ranked by the ratio of Views by Incidence\n\t\t
		among the most incident tags in the issues recorded in stackoverflow or stackexchange.\n\t\t
		The purpose of this dataframe is to use in other stages of the Project, such as, for example,\n\t\t
		the youtube data scraping parameter

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
		a DataFrame with the 'Tag', 'Incidence', 'Votes', 'Answer' and 'ViewsPerIncidence' data\n\t\t of the top 15 tags () ranked by the ratio of Views by Incidence\n\t\t
		among the most incident tags in stackoverflow or stackexchange issues

		'''
		# Empty Dictinaries
		bagOfWords = {}
		bagOfWordsVotes = {}
		bagOfWordsAnswers = {}
		bagOfWordsViews = {}

		# DataFrame with all the question that was scraped
		df = stackScrape.scrapeData(self, base_url, tag, query_filter, max_pages, pagesize)

		count = 0
		# loop on each row of the DataFrame with the questions
		for row in df['tags'].apply(lambda row: row.split()):
			# loop on each tag of the set of tags in each row of the DataFrame
			for i in row:
				# Incidence of each tag
				bagOfWords[i] = bagOfWords.get(i, 0) + 1
				# sum total of votes per tag
				bagOfWordsVotes[i] = bagOfWordsVotes.get(i, 0) + df.loc[count, 'votes']
				# sum total of answers per tag
				bagOfWordsAnswers[i] = bagOfWordsAnswers.get(i, 0) + df.loc[count, 'answer']
				# sum total of views per tag
				bagOfWordsViews[i] = bagOfWordsViews.get(i, 0) + df.loc[count, 'views']

			count += 1
		# Merge All the dictionaries into one DataFrame
		DfTags = pd.Series(bagOfWords).to_frame().rename(columns={0:'Incidence'}).reset_index()
		DfTags = pd.merge(DfTags, pd.Series(bagOfWordsVotes).to_frame().rename(columns={0:'Votes'}).reset_index(), how='left', left_on='index', right_on='index')
		DfTags = pd.merge(DfTags, pd.Series(bagOfWordsAnswers).to_frame().rename(columns={0:'Answer'}).reset_index(), how='left', left_on='index', right_on='index')
		DfTags = pd.merge(DfTags, pd.Series(bagOfWordsViews).to_frame().rename(columns={0:'Views'}).reset_index(), how='left', left_on='index', right_on='index')

		# Column Rename
		DfTags = DfTags.rename(columns={'index': 'Tag'})

		# The top 25 by the incidence
		DfTags = DfTags.sort_values('Incidence', ascending=False).head(25)
		# relation of total of vizualizations by the total of incidence

		DfTags['ViewsPerIncidence'] = DfTags['Views'] / DfTags['Incidence']

		# Exclusion of python and r as tags
		tagsFilter = ['python', 'r']
		DfTags = DfTags[~DfTags['Tag'].isin(tagsFilter)]

		# The top 15 by the relation of total of vizualizations by the total of incidence
		DfTags = DfTags.sort_values('ViewsPerIncidence', ascending=False).head(15)	

		return DfTags