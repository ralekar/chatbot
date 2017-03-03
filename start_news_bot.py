import os
import time
from slackclient import SlackClient
import urllib2,json
from aylienapiclient import textapi

SUMMARY_APP_NAME = 'SDSRA_1'
SUMMARY_APP_ID = 'f99d0f64'
SUMMARY_APP_KEY = '85a678c08a333c2746b5062bfebb6775'

# starterbot's ID as an environment variable
BOT_ID ='U41MFDS82' # os.environ.get("BOT_ID")
SLACK_BOT_TOKEN = 'xoxb-137729468274-nE42BHXg5grCCLmdrdPbOCs3'
# constants
AT_BOT = "<@" + BOT_ID + ">"
SUMMARY_COMMAND = "summarize"
NEWS_COMMAND = 'hook me up'

# latest , top 
source_dict = { "tech crunch": "techcrunch" , "techcrunch" : "techcrunch" , "tech-crunch" : "techcrunch" , "reuters" : "reuters" , "hackernews" : "hacker-news","business insider" :"business-insider" }
sortby_dict = { "top": "top" ,"latest":"latest" } 
source = "techcrunch"
sortby = "latest"


# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

news_api_key = '3915fa98b65d4afa8ee7dc9c9ab26d1a'
news_url = 'https://newsapi.org/v1/articles'
diffbot_url = 'https://api.diffbot.com/v3/article'
diffbot_token = '5183118dacef913be45ea51e99e35466'
summaryClient = textapi.Client(SUMMARY_APP_ID, SUMMARY_APP_KEY)




def get_summary( text , title ):
    
   summary = summaryClient.Summarize({'text': text,'title' : title, 'sentences_number': 3})
   return "".join(summary['sentences'])
   


def get_articles(source , sortby):
        
    url = news_url+"?source="+source+"&sortBy="+sortby+"&apiKey="+news_api_key
    articles = []    
    result = urllib2.urlopen(url)
    data = json.load(result)
    for article in data['articles']:
        articles.append(article['url'])
    return articles

def get_article_text(source_url):
    url = diffbot_url+"?token="+diffbot_token+"&url="+source_url
    result = urllib2.urlopen(url)
    data = json.load(result)
    text = data['objects'][0]['text']
    title = data['objects'][0]['title'] 
    text  = text.encode('ascii', 'ignore').decode('ascii')
    title = title.encode('ascii', 'ignore').decode('ascii')
    return text,title 
    #return data['objects'][0]['pageUrl']
    #return data['objects'][0]['text']
   


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. For getting news articles from source like techcrunch , business insider , reuters , hackernews SAMPLE -  *" + NEWS_COMMAND + \
               "* with the latest / top news from techcrunch . Also to summarize them , SAMPLE - *"+SUMMARY_COMMAND+"* the latest news from business insider "
    import time
    if command.startswith(NEWS_COMMAND):
        print command
        source , sortby = set_source_sort(command)
        print source , sortby , "************************"
        urls = get_articles(source , sortby)   
          
        for u in urls[:3]: 
                response = u
        	slack_client.api_call("chat.postMessage", channel=channel,
                               text=response, as_user=True)
    elif command.startswith(SUMMARY_COMMAND):
        print command
        source , sortby = set_source_sort(command)
        urls = get_articles(source , sortby)
        for url in urls[:3]: 
                text, title = get_article_text(url) 
        	response = get_summary(text,title)
                response = "*"+title+"*\n"+response 
        	slack_client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)
                time.sleep(3)
    else:
       slack_client.api_call("chat.postMessage", channel=channel,
                               text=response, as_user=True)
    

def set_source_sort( text ):
   
    source = "techcrunch"
    srt = "latest"
    for s in source_dict:
        print s
        if s in text :
           src = source_dict[s]
           break
    for s in sortby_dict:
        print s
        if s in text :
           srt = sortby_dict[s]
           break
    if src :
       source = src
    if srt :
       sortby = srt
    return (source , sortby)
        


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

'''
a = get_articles("the-next-web" , "latest")
g = get_article_text(a[0])
k = g[0].encode('ascii', 'ignore').decode('ascii')
t = g[1].encode('ascii', 'ignore').decode('ascii')
get_summary(k,t)
'''
