import sys
import pandas as pd
import youtube_dlc
import inflection

sys.path.append('../')

from stack.Stack import stackScrape

class YoutubeData(object):
	
	def __init__(self):
		self.stack = stackScrape()
	
	def renameStackColumns(self, dfStack):
		for col in dfStack.columns:
			dfStack = dfStack.rename(columns={col: col + "Stack"})
		return dfStack
	
	def camelizeColumns(self, dfResult):
		camelize = lambda col: inflection.camelize(col)
		newColumns = list(map(camelize, dfResult.columns))
		# rename
		dfResult.columns = newColumns
		return dfResult
	
	def mergeYotubeStackData(self, dfYoutube, dfStack):
		dfResult = pd.merge(dfYoutube, dfStack, how='left', left_on='Query', right_on='TagStack')
		dfResult = YoutubeData.camelizeColumns(self, dfResult)
		dfResult = dfResult.sort_values('UploadDate')
		return dfResult
	
	
	
	def getData(self, base_url, tag, query_filter, max_pages, pagesize):
    
		ydl = youtube_dlc.YoutubeDL({'ignoreerrors':True})
		dfStack = self.stack.TagsStack(base_url, tag, query_filter, max_pages, pagesize)

		dfStack = YoutubeData.renameStackColumns(self, dfStack)

		arrayQuery = dfStack['TagStack'].to_list()

		results = list()
		for query in arrayQuery:
			queryConcat = query + ' python'
			r = ydl.extract_info('ytsearchdate1:\{}'.format(queryConcat), download=False)
			for entry in r['entries']:
				if entry is not None:
					entry['Query'] = query
			results += r['entries']
		results = [e for e in results if e is not None]
		dfYoutube = pd.DataFrame(results)

		dfResult = YoutubeData.mergeYotubeStackData(self, dfYoutube, dfStack)

		return dfResult