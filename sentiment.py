import pandas as pd
nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from textblob import TextBlob
import string
import re
import settings


class SA:
    def __init__(self):
        dname = f'{settings.dbname}.csv'
        self.dataname = dname
        self.data = None
        self.cleaned_data = None
        self.read_data()
        self.preprocessing()
        self.compute_polarity()
    
    def read_data(self):
        self.data = pd.read_csv(f'{self.dataname}')
     
    
    def preprocessing(self):
        # drop the news  with missing headlines
        self.cleaned_data = self.data.dropna()

        self.cleaned_data = self.cleaned_data[~self.cleaned_data['headline'].str.isnumeric()]  # ignore the numeric headlines

        # remove unwated charecters
        self.cleaned_data['headline'] = self.cleaned_data['headline'].apply(lambda h: re.sub(r"[-()#/@;:<>{}`+=~|.!?,]","",h).lower().strip())
        self.cleaned_data['headline'] = self.cleaned_data['headline'].apply(lambda h: re.sub(r'[0-9]+',"",h))


        # remove stopwords
        stops = stopwords.words('english')
        self.cleaned_data['headline'] = self.cleaned_data['headline'].apply(lambda x: ' '.join([x for x  in x.split() if x not in stops]))

        # steming
        ps = PorterStemmer()
        self.cleaned_data['headline']=self.cleaned_data['headline'].apply(lambda w:ps.stem(w))


    def compute_polarity(self):
        self.cleaned_data['polarity'] = self.cleaned_data['headline'].apply(lambda x: TextBlob(x).sentiment.polarity) 


  