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



prompt_narrative_crypto = """Given the following text:"{text}"

Create a list of crypto tokens with the corresponding narratives
and potential catalysts for each token. Use the following guidelines:

Use the format $TOKEN or TOKEN is used when mentioning a specific token in the tweets.
If no specific $TOKEN is mentioned, summarize the general narrative.
Unify information for each $TOKEN.
Include relevant information for each $TOKEN, such as market trends, news, or events.
Add potential catalysts for each token if possible.

After creating the list, structure your response as follows:

"1) $TOKEN1: [narrative]. Catalysts: [potential catalysts].
2) $TOKEN2: [narrative]. Catalysts: [potential catalysts].
.....
n) $TOKENn: [narrative]. Catalysts: [potential catalysts].
General Narrative: [general summary of market trends]."

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



