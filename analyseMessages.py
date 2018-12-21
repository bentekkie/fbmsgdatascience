#%%
import json
import re
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from wordcloud import WordCloud, STOPWORDS
from matplotlib.font_manager import FontProperties
plt.rc('font', family='DejaVu Sans') 
plt.rc('font', serif='Helvetica Neue') 
plt.rc('text', usetex='false')
prop = FontProperties(fname='/System/Library/Fonts/Apple Color Emoji.ttc')
plt.rcParams['font.family'] = prop.get_family()
plt.rcParams.update({'font.size': 10})
plt.rcParams['figure.figsize'] = [15, 10]

def fixHex(m):
    hexs = m.string[m.start():m.end()].replace("\\x","")
    hexStr = bytes.fromhex(hexs).decode('utf-8')
    return hexStr

def fixHexStr(s):
    return re.sub(r'\\x(f0)(?:\\x(..))+',lambda m: fixHex(m),bytes(s,'unicode-escape').decode('utf-8'))


def messagesPer(messages,freq):
    s = pd.DataFrame(messages)
    s['timestamp'] = s.apply(lambda x: pd.to_datetime(x['timestamp_ms'], unit='ms').tz_localize(tz='UTC', ambiguous=True).tz_convert(tz='America/Toronto'),axis=1)
    fig, ax = plt.subplots(figsize=(15,7))
    grouped = s.groupby([pd.Grouper(key='timestamp',freq=freq),'sender_name'])
    hist = grouped['content'].count()
    data = hist.unstack()
    prevPlt = None
    for name in data:
        if prevPlt is not None:
            plt.bar(data.index,data[name],width=5, bottom=data[prevPlt]).set_label(name)
        else:
            plt.bar(data.index,data[name],width=5).set_label(name)
            prevPlt = name
    plt.legend()
    ax.get_xticks()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
    fig.autofmt_xdate()

def wordcloudOf(messages):
    s = pd.DataFrame(messages)
    filteredS = s[s.content.str.contains("sent a photo")==False]
    text = filteredS['content'].str.cat(sep='\n')
    STOPWORDS.add('ok')
    STOPWORDS.add('Yea')
    STOPWORDS.add('Ye')
    STOPWORDS.add('Yes')
    STOPWORDS.add('Good')
    STOPWORDS.add('will')
    STOPWORDS.add('Oh')
    wordcloud = WordCloud(
        width=1000,
        height=1000,
        max_font_size=400,
        stopwords=STOPWORDS).generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

def messagesByHour(messages):
    s = pd.DataFrame(messages)
    s['timestamp'] = s.apply(lambda x: pd.to_datetime(x['timestamp_ms'], unit='ms').tz_localize(tz='UTC', ambiguous=True).tz_convert(tz='America/Toronto'),axis=1)
    s['hour'] = s['timestamp'].dt.hour
    grouped = s.groupby(['hour','sender_name'])
    hist = grouped['content'].count()
    data = hist.unstack().plot(kind='bar',stacked=True)


def mostCommonWordsBar(messages):
    s = pd.DataFrame(messages)
    filteredS = s[s.content.str.contains("sent a photo")==False]
    words = pd.Series(' '.join(filteredS['content']).lower().split()).value_counts()
    wordsdf = pd.DataFrame({"count":words.values},index=words.index)
    
    #print(wordsdf)
    STOPWORDS.add('ok')
    STOPWORDS.add('yea')
    STOPWORDS.add('ye')
    STOPWORDS.add('yes')
    STOPWORDS.add('good')
    STOPWORDS.add('will')
    STOPWORDS.add('oh')

    filteredWords = wordsdf[wordsdf.index.str.lower().isin(STOPWORDS)==False]

    filteredWords[:50].plot(kind="bar")
    

with open('/Users/segalbe/Downloads/message.json', 'r') as f:
    messageDump = json.load(f)


for message in messageDump['messages']:
    if 'content' in message:
        tmp = message['content']
        message['content'] = fixHexStr(message['content'])

messages = messageDump['messages']

# Messages by hour of day
#messagesByHour(messages)
# Messages in bar graph grouped by month
#messagesPer(messages,"M")
# Messages in bar graph grouped by week
#messagesPer(messages,"W")
# Most common words bar graph
#mostCommonWordsBar(messages)
# Wordcloud of common words
wordcloudOf(messages)

