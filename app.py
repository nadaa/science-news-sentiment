import pandas as pd
#import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit.components.v1 as stc
from wordcloud import WordCloud,STOPWORDS
import warnings


import scrap
import sentiment
#import scrap_multiprocessing


def func(pol: bool)-> str:
    if pol > 0:
        return "positive"
    elif pol < 0 :
        return "negative"
    else:
        return "neutral"


def plot(df:pd.DataFrame):
    '''
    Bar plot to visualize the number of positive, negarive, neutral sentiment
    Pie plot to visualize the top 10 most frequent sections
    '''
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'xy'},{'type':'domain'}]],subplot_titles=('1. Total Frequencies of Sentiments','2. Top 10 Popular Sections'))
    df['sentiment'] = df['polarity'].apply(func)
    df1 = df['section'].value_counts(sort=True,ascending=False).head(10)
    fig.add_trace(go.Bar(x=df['sentiment'].value_counts().index, y=df['sentiment'].value_counts().values,showlegend =False),row=1,col=1)
    fig.add_trace(go.Pie(labels=df1.index,values=df1.values),row=1,col=2)
    st.plotly_chart(fig,theme="streamlit", use_container_width=True)

    # draw wordcloud
    STOPWORDS.update(['may','might','will','would','can','could'])
    st.set_option('deprecation.showPyplotGlobalUse', False)
    text = ' '.join(df['headline'])
    wc = WordCloud(collocations=False,background_color='white',max_font_size=50, max_words=100,stopwords=STOPWORDS)
    wc.generate(text)
    plt.figure(figsize=(20,20))
    plt.title('Wordcloud of The News',fontsize=25)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    st.pyplot()
    
    # mean polarity per year
    
    df.date = pd.to_datetime(df.date)
    #df_year_polarity = df.groupby(df.date.dt.month)['polarity'].mean().reset_index()
    (pd.crosstab(df.date.dt.year, df['sentiment'], normalize = 'index')*100).plot(kind = 'bar', figsize = (8, 4), stacked = True)
    plt.ylabel('Percentage Polarity %')
    plt.xlabel('Year')
    plt.title('Yearly Mean Polarity',fontsize=10)
    st.pyplot(plt)


    

def main():
    warnings.filterwarnings('ignore')
    scrp = scrap.NScrap()
    #scrp = scrap_multiprocessing.NScrap()
    sen = sentiment.SA()
    st. set_page_config(layout="wide") 
    st.title('Science News Sentimet Analysis (SNSA)')
    #menu=['Home','Scrap Science News']
    #choice = st.sidebar.selectbox('Menue',menu)
       # st.subheader('Home')
    st.markdown("Data is scraped from: https://www.sciencenews.org/all-stories")
    st.markdown(""" #### This app analyzes sentiments in science news and visualizes the results """)  



    st.markdown(""" ##### 
    > Start by either visulaize the previous collected data or scrap a new data
    > - Scrap the entire website (may take long time) 
    > - Or scrap the last *n* number of pages 
                """ )  

    #st.subheader('Scrap Science News')
    option = st.radio(label='Select one option of scraping',options=['All news','Most recent news'],label_visibility='hidden')
    n_input = st.text_input(label='Number of pages to scrap',value='10')
    if st.button('Start Scraping'):
        if option == 'All news':
            scrp.get_news(None) #scrap all the pages
        else:
            scrp.get_news(int(n_input)) #scrap the last n pages      
            scrp.store_to_csv()

    if st.button(label='Visualize sentiments'):
    # st.subheader('Sentiment Analysis')
        plot(sen.cleaned_data)
            



if __name__ == '__main__':
    main()

