import requests
import configparser
import download_data
import datetime as dt
import pandas as pd
import query_data
import pytz
import schedule


def main(users,output_file = "tweets_crypto"):
    # Read config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Twitter API credentials and authentication
    channelId = config['telegram']['channelId']
    telegramApiKey = config['telegram']['api_key']

    start_date = dt.datetime.today() - dt.timedelta(days=2)
    end_date = dt.datetime.today() + dt.timedelta(days=1)
    tweets = download_data.run(users, start_date, end_date, output_file = output_file)

    # read tweets from file
    #tweets = pd.read_pickle("tweets_crypto.pkl")

    # get tweets from last 24 hours
    last_24 = dt.datetime.now(pytz.UTC) - dt.timedelta(days=1)
    tweets = [ tweet for tweet in tweets  if tweet.created_at >= last_24]

    docs = query_data.create_thread_docs(tweets,filer_len=2)

    msg = query_data.query(docs)

    messageText = f'{dt.date.today()} Last 24 hours: \n' + msg
    telegramResult = requests.get(f"https://api.telegram.org/bot{telegramApiKey}/sendMessage",
                                  params={"chat_id": channelId, "text": messageText})

    print(telegramResult)

if __name__ == "__main__":
    # users to get tweets from
    # list from here: https://twitter.com/milesdeutscher/status/1628772079272361984
    users = ['@QuantMeta', '@apes_prologue', '@CC2Ventures', '@umbrella_uni', '@milesdeutscher', '@rektfencer',
             '@CryptoShiro_', '@0xsurferboy', '@0xkyle__', '@EnzCrypto_', '@theirish_man', '@JA_Maartun', '@ali_charts',
             '@RunnerXBT', '@_FabianHD', '@__bleeker', '@0xJezza', '@imajinthesmell', '@MasalaOfCharts',
             '@PuggyTrades', '@BeraGrizzly', '@bxresearch']
    #main(users,output_file = "tweets_crypto")

    schedule.every().day.at("10:00").do(main, users, output_file = "tweets_crypto")