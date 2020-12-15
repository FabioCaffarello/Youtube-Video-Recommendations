import pandas  as pd
import sqlite3 as sql

from youtube import YoutubeData

dbName = 'youtubeVideo.db'


def updateDB():
    
    params = {
                'base_url': 'https://stats.stackexchange.com/questions/tagged/',
                'tag': 'python',
                'query_filter': 'Votes',
                'max_pages': 50,
                'pagesize': 50,
                'num_videos': 50
            }
    
    ydt = YoutubeData()
    data = ydt.getData(**params)
    with sql.connect(dbName) as conn:
        data = data[['Id', 'Title', 'WebpageUrl', 'LikeCount', 'UploadDate', 'Duration', 'IncidenceStack', 'VotesStack', 'ViewCount', 'TagStack']]
        data.to_sql(name='videos', con=conn, if_exists='replace', index=False)
        conn.commit()
    return True