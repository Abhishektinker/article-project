from flask import Flask,render_template,request
import requests
from datetime import datetime,timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


app=Flask(__name__)

def find_article(query):
    now=datetime.now()-timedelta(days=25)
    date=now.strftime('%Y-%m-%d')
    key="30e468fbe37f4d62a3d177f5315e549c"
    news_url=f"https://newsapi.org/v2/everything?q={query}&from={date}&sortBy=publishedAt&apiKey={key}"
    ny_url=f"https://api.nytimes.com/svc/search/v2/articlesearch.json?q={query}&api-key=pGJiyWkssKPx8Q7pxuFKqzGa7H8ZRkNq"
    resp1=requests.get(news_url)
    resp2=requests.get(ny_url)
    data1=resp1.json()
    data2=resp2.json()
    data1=pd.DataFrame(data1['articles'])
    data1['source']=data1['source'].apply(lambda x:x['name'])
    data2=pd.DataFrame(data2['response']['docs'])
    data2.rename({'web_url':'url','byline':'author','pub_date':'publishedAt','headline':'title','multimedia':'urlToImage','abstract':'description','lead_paragraph':'content'},axis=1,inplace=True)
    for i in data2.columns:
        if i in data1.columns:
            pass
        else:
            data2.drop([i],inplace=True,axis=1)            
    data2['author']=data2['author'].apply(lambda x:x['original'])
    data2['urlToImage']=data2['urlToImage'].apply(lambda x:"../static/1200x675_nameplate.png")
    data2['title']=data2['title'].apply(lambda x:x['main'])
    final_data=pd.concat([data1,data2],ignore_index=True)
    return final_data
    
def figures(query,column_name):
    final_data=find_article(query)
    plt.rcParams['figure.figsize']=9,4
    plt.rcParams['figure.dpi']=60
    plt.figure(facecolor='k')
    ax=plt.gca()
    final_data[column_name].value_counts()[:5].plot(kind='bar')
    ax.set(facecolor='k')
    plt.xticks(color='#FF00FF',fontsize=15,rotation=80)
    ax.spines['right'].set_color('w')
    plt.title(f'top_{column_name}',color='cyan',fontsize=20)
    plt.savefig(f'./static/{column_name}.png',bbox_inches='tight',dpi=60)    



@app.route('/')
def main():
    return render_template('index.html')

@app.route('/Articles/')
def Articles():
    df=find_article('tokyo olympics')
    urls=df['url']
    img_url=df['urlToImage']
    source=df['source']
    headline=df['title']
    l=len(df)
    return render_template('Articles.html',headline=headline,img_url=img_url,source=source,urls=urls,l=l)    

@app.route('/av_articles/',methods=['GET','POST'])
def av_articles():
    query=request.form.get('query')
    figures(query,'source')
    figures(query,'author')
    f=find_article(query)
    urls=f['url']
    img_url=f['urlToImage']
    source=f['source']
    headline=f['title']
    l=len(f)
    return render_template('av_articles.html',headline=headline,img_url=img_url,source=source,urls=urls,l=l,query=query)

@app.route('/analysis/',methods=['GET','POST'])
def analysis():
    query=request.form.get('query')
    f=find_article(query)
    top_5_title=f.sort_values(by='publishedAt')[:5][['title','url']]
    z=zip(top_5_title['title'],top_5_title['url'])
    return render_template('analysis.html',top_5_title=top_5_title,z=z)    

@app.route("/light_analysis/")
def light_analysis():
    return render_template('light_analysis.html')


app.run(debug=True,port=80)    