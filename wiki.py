import wikipediaapi
import requests
from datetime import datetime
import random
import toml
from mastodon import Mastodon
from urllib.parse import unquote
import os

class Wiki:
  def __init__(self, user_agent):
    self.wiki_client = wikipediaapi.Wikipedia(user_agent, 'en')

  def get_random_page(self):
    response = requests.get('https://en.wikipedia.org/wiki/Special:Random')
    url_title = response.url.split('/')[-1]
    url_title = unquote(url_title)
    page = self.wiki_client.page(url_title)
    return page

  def day_in_history(self, month_day, num_events=3, num_births=3, num_deaths=3):
    page = self.wiki_client.page(month_day)
    events = random.sample(random.choice(page.section_by_title('Events').sections).text.split("\n"), num_events)
    births = random.sample(random.choice(page.section_by_title('Births').sections).text.split("\n"), num_births)
    deaths = random.sample(random.choice(page.section_by_title('Deaths').sections).text.split("\n"), num_deaths)
    return [page.title, page.fullurl, events, births, deaths]

  def today_in_history(self, num_events=3, num_births=3, num_deaths=3):
   today = datetime.now()
   month_day = today.strftime("%B_%d")
   return self.day_in_history(month_day, num_events, num_births, num_deaths)

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
      updated_events += ["- *" + event + "*"]
    return '\n'.join(updated_events)

  def format_post(self):
    num_events = self.config.get("num_events")
    num_births = self.config.get("num_births")
    num_deaths = self.config.get("num_deaths")
    date, date_url, events, births, deaths = self.wiki.today_in_history(num_events, num_births, num_deaths)
    random_article = self.wiki.get_random_page()
    markdown_date = date.replace("_", " ")
    #print(date.replace("_", ""))
    #print(markdown_date)
    tag_date = markdown_date.replace(" ", "")
    #print(markdown_date.replace(" ", ""))
    events = self.format_events(events)
    births = self.format_events(births)
    deaths = self.format_events(deaths)
    summary = random_article.summary.split('\n\n', 1)[0]
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
    print(bot.format_post())
    #bot.post()
  except Exception as e:
    print(e)
    #bot.post()
  #print(bot.format_post())
