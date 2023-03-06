from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.llms import OpenAIChat
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.chains.mapreduce import MapReduceChain
import os
import configparser
import datetime as dt
from langchain.chains.summarize import load_summarize_chain
# Read config file
config = configparser.ConfigParser()
config.read('config.ini')
os.environ["OPENAI_API_KEY"] = config['openai']['api_key']


prompt_narrative_crypto = """Create a list of crypto $TOKEN from the text and follow this guide:
                             1) Tokens mentioned in the tweets should be in the format $TOKEN, but not necessarily.
                             2) Unify information for each $TOKEN.
                             3) For each $TOKEN, inclued narrative  or relevant information.
                             4) Add catalysts for each token if possible.
                             5) if No specific $TOKEN mentioned, join all the text together.
    response list example: "1) $BTC:  Posible pump due to Elon Musk's tweet. Catalyst: Next convention in march.
                       2) $HPK:  Strong narrative  Catalyst: No info.
                       3) General Narrative:
                          - Many altcoins are currently experiencing a significant drop in price.
                          - CPI data is expected to be released today.
                       "

   {text}
   """


def create_thread_docs(tweets,filer_len=2):
    threads = {}
    # sort tweets by id
    tweets = sorted(tweets, key=lambda tweet: tweet.id, reverse=False)

    # loop for tweets that are initial tweets
    for tweet in tweets:
        if tweet.in_reply_to_status_id is None:
            threads[tweet.id] = [tweet]

    for  k in threads.keys():
        tweet_id_inicial = k
        tweet_id = tweet_id_inicial
        # Add the rest of the tweets in the thread
        for tweet in tweets:
            if tweet.in_reply_to_status_id == tweet_id:
                threads[tweet_id_inicial].append(tweet)
                tweet_id = tweet.id

    # Filter, at lest 2 tweets in the thread
    threads = {k: v for k, v in threads.items() if len(v) >= filer_len}


    # Join tweets from each thread into a single string
    doc = []
    full_text = ''
    for k in threads.keys():
        screen_name = '@'+threads[k][0].user.screen_name
        thread_text = ' '.join([tweet.full_text for tweet in threads[k]])
        doc.append(Document(page_content=thread_text, metadata={'screen_name': screen_name}))
        full_text += '----' +thread_text
    return doc


def query(docs, prompt_template=prompt_narrative_crypto):
    llm = OpenAIChat(temperature=0)

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=PROMPT)
    return chain.run(docs)



