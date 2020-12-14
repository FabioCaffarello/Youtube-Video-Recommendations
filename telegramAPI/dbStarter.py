import runBackend
import sqlite3 as sql

if __name__ == '__main__':
	with sql.connect(runBackend.dbName) as conn:
		cur = conn.cursor()
		# Create Table
		cur.execute('''CREATE TABLE videos (Id TEXT UNIQUE
												,Title TEXT
												,WebpageUrl TEXT UNIQUE
												,LikeCount INTEGER
												,UploadDate DATE
												,Duration INTEGER
												,IncidenceStack REAL
												,VotesStack REAL
												,ViewCount REAL
												,TagStack TEXT
												)''')
		conn.commit()
	runBackend.updateDB()