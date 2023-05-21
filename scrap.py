import pandas as pd
import sqlite3
import requests
from bs4 import BeautifulSoup
from stqdm import stqdm
from time import sleep
import settings

class NScrap:
    def __init__(self):
        self.db = None
        self.cur = None
        self.url = settings.url
        self.df = None
        self.create_db()
        

    def create_db(self):
        '''
        Create sqlite3 database
        '''
        try:
            self.db = sqlite3.connect(settings.dbname)
            self.cur = self.db.cursor()
            # DROP TABLE
            self.cur.execute("""DROP TABLE IF EXISTS 'settings.table_name'""")
            # create a table
            self.cur.execute('''CREATE TABLE 'settings.table_name'(section TEXT,headline TEXT, description TEXT, author TEXT, date Time)''')
        except sqlite3.Error as err:
             print('Sql error: %s' % (' '.join(err.args)))
             print("Exception class is: ", err.__class__)

        
    def insert_to_db(self, news:list) -> None:
        '''
        Insert values to the database
        
        '''
        for i in range(len(news)):
            section = news[i][0]
            headline = news[i][1]
            description = news[i][2]
            author = news[i][3]
            date = news[i][4]
            try:
                self.cur.execute(
                """INSERT INTO news(section,headline, description, author, date) VALUES(?,?,?,?,?)""", (section,headline, description, author, date))
            except sqlite3.Error as err:
                print('Sql error: %s' % (' '.join(err.args)))
                print("Exception class is: ", err.__class__)

                
    def get_html(self,url : str) -> str:
        '''
        Read the html page
        '''
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        res = ''
        try:
            res =  requests.get(url,headers=headers)
        except requests.exceptions.HTTPError as http_error:
            print(http_error)
        else:
             pass 
        return res

    
    def get_num_pages(self) -> int:
        '''
        Grab the number of pages from the website
        '''
        page = self.get_html(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        num_pages =max([int(p.text.replace(',','')) for p in soup.find_all("a",class_="page-numbers") if p.text!='Next'])
        return num_pages


    def get_news(self,n_pages:int)-> None :
        '''
         Parse the html page and collect the news
        
        '''
        if not n_pages:
            n_pages = self.get_num_pages()
        
        for p in stqdm(range(n_pages)):
            news_per_page = []
            p_url = f'{self.url}/page/{p}'
            try:
                page = self.get_html(p_url)
                page.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print('Bad status code', page.status_code)
                
            soup = BeautifulSoup(page.content,'html.parser')
            news_div = soup.find_all('div',class_='post-item-river__content___ueKx3')
                
            for div in news_div:
                section = div.find('a',class_='post-item-river__eyebrow___Zir4H')
                headline = div.find('h3',class_='post-item-river__title___vyz1w')
                description = div.find('p',class_='post-item-river__excerpt___SWLb7')
                author =  div.find('a',class_='byline-link url fn n')
                date  =  div.find('time',class_='post-item-river__date___9SCxt entry-date published')
                    
                if section!= None:
                    section = section.text.strip()
                if headline!=None:
                    headline = headline.text.strip()
                if description!=None:
                    description = description.text.strip()
                if author!=None:
                    author = author.text.strip()
                if date!=None:
                    date = date.text.strip()                    
                news_per_page.append((section,headline,description,author,date))
           # store the news in the db 
            sleep(0.5)
            self.insert_to_db(news_per_page)
        print('End of scraping')



    def handle_date(self):
        """
        Fix incosistency in date column
        """
        from datetime import date
        # if there is "ago" in the date, replace the string by the current date
        # convert string date into date
        today = date.today()
        self.df['date'] = self.df['date'].str.replace(r'(^.*ago.*$)', today.strftime("%B %d, %Y"))
        self.df.date = pd.to_datetime(self.df.date)


    def store_to_csv(self):
        """
        Save the database as a csv file
        """
        df = pd.read_sql_query("SELECT * FROM news", self.db)
        if len(df)>0 :
            self.df = df
            self.handle_date()
            self.df.to_csv(settings.outputfile,index=False)


