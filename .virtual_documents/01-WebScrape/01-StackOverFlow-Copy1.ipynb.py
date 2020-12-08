import re
import time
import requests
import pandas as pd

from bs4 import BeautifulSoup


class StackOverflow():    
  
    def __init__():
        pass

    def extract_data_from_url(url):
        
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        data = StackOverflow.parse_tagged_page(soup)
        return data

    def clean_scraped_data(text , keyname=None):
        if keyname == 'votes':
            return text.replace('\nvotes', '')
        elif keyname == 'answer':
            return text.replace('answers', '')
        return text
    
    def get_id(q):
        
        pattern = 'href="/questions/([^"]+)[\/]'
        q_id = re.search(pattern,q).group(1)
        return q_id
    
    
    def parse_tagged_page(soup):
        question_summaries = soup.select('.question-summary')
        key_names = ['question', 'votes', 'tags','answer']
        classes_needed = ['.question-hyperlink', '.vote', '.tags', '.status']
        datas = []
        for q_el in question_summaries:
            question_data = {}
            for i, _class in enumerate(classes_needed):
                sub_el = q_el.select(_class)[0]
                keyname = key_names[i]
                question_data[keyname] = StackOverflow.clean_scraped_data(sub_el.text.strip(), keyname=keyname)
                if _class == '.question-hyperlink':
                    question_data['id'] = StackOverflow.get_id(str(sub_el))
            datas.append(question_data)
            
        return datas
    
    
    def scrape_data(tag, query_filter, max_pages, pagesize):
        
        base_url = 'https://stackoverflow.com/questions/tagged/'
        datas = list()
        for p in range(max_pages):
            page_num = p + 1
            url = f'{base_url}{tag}?tab={query_filter}&page={page_num}&pagesize={pagesize}'
            datas += StackOverflow.extract_data_from_url(url)
            time.sleep(0.5)
        return datas


parameter_url = {'tag' :'python',
'query_filter' :'votes',
'max_pages' :4,
'pagesize' :25}


scrape_data = StackOverflow.scrape_data(**parameter_url)


dfStackOverFlor = pd.DataFrame(scrape_data, columns=scrape_data[0].keys())


dfStackOverFlor.head()
