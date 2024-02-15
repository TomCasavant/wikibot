import wikipediaapi
import requests
from datetime import datetime
import random
import toml
from mastodon import Mastodon
from urllib.parse import unquote
import os
from bs4 import BeautifulSoup

class Day:

  def __init__(self, page):
    self.wiki_page = page
    self.url = page.fullurl
    self.title = page.title
    self.births = self.find_births()
    self.deaths = self.find_deaths()
    self.events = self.find_events()
    self.holidays = self.find_holidays()

  def find_births(self):
    births = []
    for time_period in self.wiki_page.section_by_title('Births').sections:
      births += time_period.text.split("\n")
    return births

  def find_deaths(self):
    deaths = []
    for time_period in self.wiki_page.section_by_title('Deaths').sections:
      deaths += time_period.text.split("\n")
    return deaths

  def find_events(self):
    events = []
    for time_period in self.wiki_page.section_by_title('Events').sections:
      events += time_period.text.split("\n")
    return events

  def find_holidays(self):
    return self.parse_holiday_tags(self.wiki_page.section_by_title('Holidays and observances').text)

  def get_events(self, count=3):
    return random.sample(self.events, count)

  def get_births(self, count=3):
    return random.sample(self.births, count)

  def get_deaths(self, count=3):
    return random.sample(self.deaths, count)

  def get_holidays(self, count=3):
    return random.sample(self.holidays, count)

  def parse_holiday_tags(self, html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for element in soup.children:
      for child in element.children:
        if (child.text != "\n"):
          items += child
    return items[2:] # Temporary solution to the Christian feast days

class Wiki:
  def __init__(self, user_agent):
    self.wiki_client = wikipediaapi.Wikipedia(user_agent, 'en', extract_format=wikipediaapi.ExtractFormat.HTML)

  def get_random_page(self):
    response = requests.get('https://en.wikipedia.org/wiki/Special:Random')
    url_title = response.url.split('/')[-1]
    url_title = unquote(url_title)
    page = self.wiki_client.page(url_title)
    return page

  def today_in_history(self):
   current_date = datetime.now()
   month_day = current_date.strftime("%B_%d")
   page = self.wiki_client.page(month_day)
   today = Day(page)
   return today

class WikiBot:

  def __init__(self) -> None:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.toml')
    with open(config_path, 'r') as config_file:
      self.config = toml.load(config_file)
      self.server = self.config.get("server")
      self.access_token = self.config.get("access_token")
      self.mastodon = self.login()
      self.wiki = Wiki(self.config.get("user_agent"))

  def login(self):
    return Mastodon(access_token=self.access_token, api_base_url=self.server)

  def format_events(self, events):
    updated_events = []
    for event in events:
      event = event.replace("<ul>","").replace("<li>","").replace("<li>","").replace("</ul>", "")
      updated_events += ["- *" + event + "*"]
    return '\n'.join(updated_events)

  def format_summary(self, text):
    return BeautifulSoup(text, 'html.parser').get_text()

  def format_post(self):

    num_events = self.config.get("num_events")
    num_births = self.config.get("num_births")
    num_deaths = self.config.get("num_deaths")

    today = self.wiki.today_in_history()
    date = today.title
    date_url = today.url
    random_article = self.wiki.get_random_page()
    markdown_date = date.replace("_", " ")

    tag_date = markdown_date.replace(" ", "")

    events = self.format_events(today.get_events(num_events))
    births = self.format_events(today.get_births(num_births))
    deaths = self.format_events(today.get_deaths(num_deaths))
    holidays = self.format_events(today.get_holidays(3))
    summary = self.format_summary(random_article.summary.split('\n\n', 1)[0])

    article_title = random_article.title.replace("_", " ")
    tags = " ".join(["#wikipedia", f"#{tag_date}", f"#{article_title.replace(' ', '').replace('-','')}"])
    return (
        f"# [{markdown_date}]({date_url})\n"
        "**This day in history**:\n"
        f"{events}\n\n"
        "**Births:**\n"
        f"{births}\n\n"
        "**Deaths:**\n"
        f"{deaths}\n\n"
        "**Holidays:**\n"
        f"{holidays}\n\n"
        "**Random Article of the day:**\n"
        f"### [{random_article.title.replace('_', ' ')}]({random_article.fullurl})\n"
        f"> {summary}\n"
        f"{tags}"
    )

  def post(self):
    message = self.format_post()
    print(message)
    self.mastodon.status_post(message) #, content_type='text/markdown')

#get_random_page()
#today_in_history()
#print(format_post())

if __name__ == '__main__':
  bot = WikiBot()
  try:
    #print(bot.format_post())
    bot.post()
  except Exception as e:
    print(e)
    bot.post() # Temporary solution for error handling (e.g. server didn't respond)
  #print(bot.format_post())
