import os
import json
import requests
import sqlite3 as sql
import pandas as pd

from flask import Flask, request, Response

import runBackend

runBackend.dbName

# Contants
# Documentation: https://core.telegram.org/bots/api
TOKEN = "1419534321:AAEqQvXs-dhyh0IWdVy9VCINO1aA15kDOd4"

# # Info about the Bot
# https://api.telegram.org/bot{TOKEN}/getMe

# # Get Update
# https://api.telegram.org/bot{TOKEN}/getUpdates
#{"ok":true,"result":[{"update_id":571661109,
# "message":{"message_id":3,"from":{"id":1476417204,"is_bot":false,"first_name":"Fabio","last_name":"Caffarello","language_code":"pt-br"},"chat":{"id":1476417204,"first_name":"Fabio","last_name":"Caffarello","type":"private"},"date":1607390409,"text":"Oi amigo"}}]}

# # WebHook
# https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://youtube-telegram.herokuapp.com/

# # Send Message
# https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id&text=Oi amigo!!
# https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=1476417204&text=Oi amigo!!
#{"ok":true,"result":{"message_id":4,"from":{"id":1353530992,"is_bot":true,"first_name":"RossmannBot","username":"RossmannPredictBot"},"chat":{"id":1476417204,"first_name":"Fabio","last_name":"Caffarello","type":"private"},"date":1607390633,"text":"Oi amigo!!"}}

def getTags():
	with sql.connect(runBackend.dbName) as conn:
		tags = pd.read_sql_query(('SELECT DISTINCT TagStack FROM videos'), conn)
	return tags['TagStack'].to_list()


def parseMessage(message):
	chat_id = message['message']['chat']['id']
	tag = message['message']['text']

	tag = tag.replace( '/', '' )
	tag = str(tag)

	return chat_id, tag


def loadDataset(tag):
	# Loding test and store dataset
	with sql.connect(runBackend.dbName) as conn:
		df = pd.read_sql_query(('SELECT DISTINCT Id, Title, WebpageUrl, LikeCount, UploadDate, Duration, IncidenceStack, VotesStack, ViewCount, TagStack FROM videos WHERE TagStack = "{}"'.format(tag)), conn)

		# Convert DataFrame to JSON
		data = json.dumps(df.to_dict(orient='records'))

	return data


def sendMessage(chat_it, text):
	url = 'https://api.telegram.org/bot{}/'.format(TOKEN)
	url += 'sendMessage?chat_id={}'.format(chat_it)

	r = requests.post(url, json={'text': text})
	print('Status Code {}'.format(r.status_code))

	return None



def predict(data):
	## API Call
	url = 'https://youtube-video-recommendations.herokuapp.com/video/predict'
	header = {'Content-Type': 'application/json'}
	data = data

	r = requests.post(url, data=data, headers=header)
	#print('Status Code {}'.format(r.status_code))

	dfResponse = pd.DataFrame(r.json(), columns=r.json()[0].keys())
	dfResponse = dfResponse.sort_values('Predict', ascending=False)
	return dfResponse.head()



# API initialize
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		message = request.get_json()

		chat_id, tag = parseMessage(message)
		
		
		if tag in getTags():
			data = loadDataset(tag)
			dfResponse = predict(data)
			# Send Message
			msg = 'The selection with the top 5 videos related to {} are:\n'.format(tag)
			for row in range(5):
				msg += '\n- Title:{}\n- chances to like: {:,.2f}%\nLink: {}\n'.format(
						dfResponse.iloc[row, 0],
						dfResponse.iloc[row, 2]*100,
						dfResponse.iloc[row, 1])
			sendMessage(chat_id, msg)
			return Response('Ok', status=200)
		else:
			if tag == 'TagList':
				tags = getTags()
				msg = 'Tags available with the most recurrent and relevant subjects in StackExchange:\n'
				for tag in tags:
					msg += '-{};\n'.format(tag)
				sendMessage(chat_id, msg)
				return Response('Ok', status=200)
			else:
				sendMessage(chat_id, 'Tag not available for consultation. To see which tags are available type /TagList')
				return Response('Ok', status=200)	
			
	else:
		return '<h1> Youtube Telegram Bot </h1>'
		return Response('Ok', status=200)		
			

if __name__ == '__main__':
	app.run(host='0.0.0.0')