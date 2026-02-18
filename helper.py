import pandas as pd
import numpy as np
import re
from urlextract import URLExtract
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter 
import emoji
from datetime import date as dte

def preprocessor(data):
    data = data.replace('\u202f',' ')
    data = data.replace('\n','')
    pattern = '(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM))\s-\s'
    messages = re.split(pattern,data)[::2][1:]
    date = re.split(pattern,data)[1::2]

    df = pd.DataFrame(messages,columns=['user_messages'])
    df['date'] = pd.to_datetime(date,errors='coerce')
    df.dropna(inplace=True)

    user = []
    messages =[]

    for msg in df['user_messages']:
        entry = re.split('(.*?):\s',msg)

        if entry[1:]:
            user.append(entry[1])
            messages.append(entry[2])
        else:
            user.append('group notification')
            messages.append(entry[0])
    
    df['user'] = user
    df['message'] = messages
    df.drop('user_messages',axis=1,inplace=True)
    df['year'] = df['date'].dt.year
    df["month_num"] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['min'] = df['date'].dt.minute

    # fixing date
    df = df[df['year'] >= 2000]
    df = df[df['date'].dt.date <= dte.today()]

    # period calculation
    period = []
    for hour in df[['day_name','hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + "00")
        elif hour == 0:
            period.append("00" + "-" + str(hour+1))
        else:
            period.append(str(hour) + "-" + str(hour+1))
    
    df['period'] = period
  
    return df

def fetch_stat(selected_user,df):
    if selected_user !=  'All':
        df = df[df['user']==selected_user]
    
    total_msg = df.shape[0]
    media_shared = len(df[df['message']=="<Media omitted>"])
    total_words = len(" ".join(df['message']).split()) - (2 * media_shared)

    all_links = []
    extractor = URLExtract()
    for msg in df['message']:
            links = list(extractor.gen_urls(msg))
            if links:
                all_links.extend(links)

    return total_msg,total_words,media_shared,len(all_links)


def busy_users(df):
    # bar graph
    x = df[df['user'] != 'group notification']['user'].value_counts().head()
    fig , ax = plt.subplots()
    ax.bar(x.index,x.values,color='green')
    plt.xticks(rotation='vertical')

    # percentages
    new_df = round(df['user'].value_counts().apply(lambda x : x / df.shape[0]) * 100,2)
    new_df.rename("percentage %",inplace=True)
    return fig , new_df 

def create_wordcloud(selected_user,df):
    if selected_user !=  'All':
        df = df[df['user']==selected_user]
    else:
        df = df[df['user']!="group notification"]

    wc = WordCloud(height=700,width=700,background_color='white',min_font_size=10)
    df_wc = wc.generate(df[df['message'] != "<Media omitted>"]['message'].str.cat(sep=" "))
    return df_wc

def most_freq_words(selected_user,df):
    if selected_user !=  'All':
        df = df[df['user']==selected_user]
    else:
        df = df[df['user']!="group notification"]
    
    temp = " ".join(df[df['message'] != "<Media omitted>"]['message']).lower().split()

    with open('stop_hinglish.txt','r') as f:
        stop_words = f.read().split(sep='\n')

    words = []
    for word in temp:
        if word not in stop_words:
            words.append(word)
    
    count_df = pd.DataFrame(Counter(words).most_common(20))
    
    return count_df

def count_emoji(selected_user,df):
    if selected_user !=  'All':
        df = df[df['user']==selected_user]
    
    emojis =[]

    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_count = pd.DataFrame(Counter(emojis).most_common(20))

    return emoji_count

def monthly_timeline(selected_user,df):
    if selected_user !=  'All':
        df = df[df['user']==selected_user]
    
    timeline = df.groupby(['year','month_num','month'])['message'].count().reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def activity_map(selected_user,df):
    if selected_user !=  'All':
        df = df[df['user']==selected_user]
    
    busy_day = df['day_name'].value_counts()
    busy_month = df['month'].value_counts()
    return busy_day , busy_month

def active_hours(selected_user,df):
    if selected_user !=  'All':
        df = df[df['user']==selected_user]
    
    pivot = pd.pivot_table(data=df,index='day_name',columns='period',values='message',aggfunc='count',fill_value=0)

    return pivot