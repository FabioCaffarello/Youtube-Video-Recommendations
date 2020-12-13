import sys
import inflection
import youtube_dlc

import pandas as pd

from stack.Stack import stackScrape


sys.path.append('../')




class YoutubeData(object):
	
	def __init__(self):
		# stackScrape class initialization
		self.stack = stackScrape()
	
	def renameStackColumns(self, dfStack):
		'''
		returns the dataframe with all renamed columns (adds the string 'Stack' to each column)
		
		Parameters
		----------
		dfStack: DataFrame that is obtained by scraping the stackoverflow or stackexchange site
		
		Return
		------
		A DataFrame
		'''
		# loop in each column of the DataFrame
		for col in dfStack.columns:
			dfStack = dfStack.rename(columns={col: col + "Stack"})
			
		return dfStack
	
	def camelizeColumns(self, dfResult):
		'''
		returns the DataFrame with the columns renamed according to the camelize pattern.
		
		Parameters
		----------
		dfResult: DataFrame that is merged with youtube and stackoverflow or stackexchange data.
		
		Return
		------
		A DataFrame
		'''
		# lambda function to camelize pattern
		camelize = lambda col: inflection.camelize(col)
		# list with all the columns of the DataFrame with camelize pattern
		newColumns = list(map(camelize, dfResult.columns))
		# DataFrame columns rename
		dfResult.columns = newColumns
		
		return dfResult
	
	def mergeYotubeStackData(self, dfYoutube, dfStack):
		'''
		returns a dataframe with information from youtube and satckoverflow or stackexchenge.
		
		Parameters
		----------
		dfYoutube: DataFrame with information from youtube.
		dfStack: DataFrame with information from satckoverflow or stackexchenge.
		
		Return
		------
		A DataFrame
		'''
		# Merge DataFrame
		dfResult = pd.merge(dfYoutube, dfStack, how='left', left_on='Query', right_on='TagStack')
		# Columns rename with the camelize pattern
		dfResult = YoutubeData.camelizeColumns(self, dfResult)
		# sorting by date of update
		dfResult = dfResult.sort_values('UploadDate')
		
		return dfResult
	
	
	
	def getData(self, base_url, tag, query_filter, max_pages, pagesize, num_videos):
		'''
		returns a dataframe with information from youtube and satckoverflow or stackexchenge that was scrapped.
		
		Paramaters
		----------
		base_url: url path to all question filter by a tag >> parameter to stackScrape class
					- stackexchange: https://stats.stackexchange.com/questions/tagged/
					- stackoverflow: https://stackoverflow.com/questions/tagged/

		tag: tag to be filtered (e.g.: 'python', 'r', 'javascript', ...) >> parameter to stackScrape class

		query_filter: filter to perform a query ('Newest', 'Active', 'Bounties', 'Unanswered', 'Frequent', Votes') >> parameter to stackScrape class

		max_pages: the maximum number of pages to be scraped >> parameter to stackScrape class

		pagesize: the number of records per page (the maximum number is 50) >> parameter to stackScrape class
		
		num_videos: Number of videos in each query for youtube scrapping
		
		Return
		------
		A DataFrame
		'''		
		# YoutubeDL class initialization
		ydl = youtube_dlc.YoutubeDL({'ignoreerrors':True})
		
		# Getting Stack data
		dfStack = self.stack.TagsStack(base_url, tag, query_filter, max_pages, pagesize)
		
		# Rename columns of Stack DataFrame
		dfStack = YoutubeData.renameStackColumns(self, dfStack)
		
		# Array of tags for the youtube query
		arrayQuery = dfStack['TagStack'].to_list()

		results = list()
		# loop in each tag of the array of tags
		for query in arrayQuery:
			# Append string python for getting video with python relation 
			queryConcat = query + ' python'
			# Extract info from Youtube
			r = ydl.extract_info('ytsearchdate{}:\{}'.format(num_videos, queryConcat), download=False)
			# loop in each result of the extraction 
			for entry in r['entries']:
				# Add the Query Column into Dataframe
				if entry is not None:
					entry['Query'] = query
			# Append all the videos of each tag into a list		
			results += r['entries']
		# Exclude None	
		results = [e for e in results if e is not None]
		# DataFrame
		dfYoutube = pd.DataFrame(results)
		# Merge Stack and Youtube Dataframe
		dfResult = YoutubeData.mergeYotubeStackData(self, dfYoutube, dfStack)
		return dfResult