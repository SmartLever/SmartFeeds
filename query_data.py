from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
import os
import configparser
import datetime as dt
from langchain.chains.summarize import load_summarize_chain
# Read config file
config = configparser.ConfigParser()
config.read('config.ini')
os.environ["OPENAI_API_KEY"] = config['openai']['api_key']


prompt_narrative_crypto = """Create a list of the main crypto tokens and their narratives mentioned in the tweets:

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
    docs = []
    for k in threads.keys():
        screen_name = '@'+threads[k][0].user.screen_name
        thread_text = ' '.join([tweet.full_text for tweet in threads[k]])
        docs.append(Document(page_content=thread_text, metadata={'screen_name':screen_name}))

    return docs


def query(docs, prompt_template=prompt_narrative_crypto):
    llm = OpenAI(temperature=0)

    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=PROMPT)
    return chain.run(docs)
