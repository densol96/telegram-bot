import requests
import datetime as dt
import os 

STOCK = "TSLA"
COMPANY_NAME = "Tesla"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_ID = os.environ.get("TELEGRAM_BOT_ID")


def get_stock_data():
    api_endpoint = "https://www.alphavantage.co/query?"
    parameters = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": STOCK,
        "apikey": STOCK_API_KEY
    }
    response = requests.get(url=api_endpoint, params=parameters)
    response.raise_for_status()
    return response.json()["Time Series (Daily)"]

def get_news(from_date, to_date):
    api_endpoint = "https://newsapi.org/v2/everything?"
    parameters = {
        "apiKey": NEWS_API_KEY,
        "q": COMPANY_NAME,
        "searchIn": "title",
        "from": from_date,
        "to": to_date
    }
    response = requests.get(url=api_endpoint, params=parameters)
    response.raise_for_status()
    return response

def telegram_bot_sendtext(articles, percent):
    bot_token = TELEGRAM_BOT_TOKEN
    bot_chatID = TELEGRAM_BOT_ID
    bot_message = ""

    if percent > 0:
        bot_message = f"{STOCK} Up by {percent:1.2f}\n\n"
    elif percent < 0:
        bot_message = f"{STOCK} Down by {percent:1.2f}\n\n"

    for article in articles:
        title = "Headline: " + article["title"]
        description = "Brief: " + article["description"]
        link = f'Link: [{article["url"]}]({article["url"]})'

        bot_message += title + "\n" + description + "\n" + link + "\n\n"                                

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    requests.get(url=send_text)

dictionary = get_stock_data()
values_list = [value for key, value in dictionary.items()]
yesterday_closing_price = float(values_list[0]["4. close"])
day_before_yesterday_closing_price = float(values_list[1]["4. close"])
price_difference = yesterday_closing_price - day_before_yesterday_closing_price
percent_diff = (price_difference/yesterday_closing_price)*100

if abs(percent_diff) > 0.5:
    date = dt.datetime.now()
    year = date.year
    month = date.month
    day = date.day
    yesterday_date = f"{year}-{month:0=2d}-{day-1:0=2d}"
    before_yesterday_date = f"{year}-{month:0=2d}-{day-2:0=2d}"
    news_data = get_news(before_yesterday_date, yesterday_date)
    articles = news_data.json()["articles"]
    three_articles = articles[:2]
    telegram_bot_sendtext(three_articles, percent_diff)



