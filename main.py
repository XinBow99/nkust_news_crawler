import requests
from bs4 import BeautifulSoup
import re
import json
import time

class NKUST:
    def __init__(self):
        self.host = "https://www.nkust.edu.tw/p/"
        self.lang = "zh-tw"

        self.site_config = {
            "hot_news": f"{self.host}403-1000-1363-page.php?Lang={self.lang}",
            "honors": f"{self.host}403-1000-13-page.php?Lang={self.lang}",
            "activity" : "https://ws1.nkust.edu.tw/Activity/#",
            "about": "https://www.nkust.edu.tw/p/412-1000-617.php"
        }
    
    def write_to_json(self, file_name, data):
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print(f'{file_name} saved')

    def get_target_news_url(self, news_type, max_page=-1):
        target_url = self.site_config[news_type]
        first_page = requests.get(target_url.replace('page','1'))
        soup = BeautifulSoup(first_page.text, 'html.parser')
        last_page = int(re.findall(r'\d+', soup.find('span', class_='pg-txt').text)[0]) if max_page == -1 else max_page
        total_news_url = []

        for page_num in range(1, last_page+1):
            page_url = target_url.replace('page', str(page_num))
            page = requests.get(page_url)
            soup = BeautifulSoup(page.text, 'html.parser')
            news_list = soup.find_all('div', class_='listBS')
            print(f"Page {page_num} has {len(news_list)} news")
            for news in news_list:
                title = news.find('div', class_='mtitle')
                href = title.find('a')['href']
                total_news_url.append(href)
        print(f"Total {len(total_news_url)} news")
        return total_news_url
    
    def get_target_news_content(self, news_url):
        html_content = requests.get(news_url).text
        soup = BeautifulSoup(html_content, 'html.parser')

        title = soup.find('h2', class_='hdline').text.strip()
        mcont = soup.find('div', class_='mcont')
        ptinfoproperty_date = mcont.find('span', class_='ptinfoproperty_date')
        ptinfoproperty_date = '' if ptinfoproperty_date is None else ptinfoproperty_date.find('span').text.strip()
        mcont_p = mcont.find_all('p')
        content = ''.join(p.text.strip() for p in mcont_p)
        return {
            'title': title,
            'url': news_url,
            'date': ptinfoproperty_date,
            'content': content
        }

    def get_hot_news(self, max_page=-1):
        hot_news_url = self.get_target_news_url('hot_news', max_page)
        news_storage = []
        for url in hot_news_url:
            result = self.get_target_news_content(url)
            news_storage.append(result)
            print(f"{result['date']} {result['title']}")
        save_file_name = f'hot_news_{time.strftime("%Y%m%d-%H%M%S")}.json'
        self.write_to_json(save_file_name, news_storage)
    
    def get_honors(self, max_page=-1):
        honors_url = self.get_target_news_url('honors', max_page)
        news_storage = []
        for url in honors_url:
            result = self.get_target_news_content(url)
            news_storage.append(result)
            print(f"{result['date']} {result['title']}")
        save_file_name = f'honors_{time.strftime("%Y%m%d-%H%M%S")}.json'
        self.write_to_json(save_file_name, news_storage)
    
    def get_activity(self, max_item=-1):
        activity_url = self.site_config['activity']
        Snos = list(set(re.findall(r'Sno=(.*)"', requests.get(activity_url).text))) if max_item == -1 else Snos[:max_item]
        news_storage = []
        for Sno in Snos:
            _url = f"https://ws1.nkust.edu.tw/Activity/Home/Event?Sno={Sno}"
            result = requests.get(_url).text
            title = re.sub(r'&#\d+;|&\w+;', '', re.findall(r'<h2>(.*)</h2>', result)[0])
            soup = BeautifulSoup(result, 'html.parser')
            content = re.sub(r'&#\d+;|&\w+;', '', soup.find('div', class_='blog-main').text.strip())
            print(f"{title}")
            news_storage.append({
                'title': title,
                'url': _url,
                'content': content
            })
        save_file_name = f'activity_{time.strftime("%Y%m%d-%H%M%S")}.json'
        self.write_to_json(save_file_name, news_storage)
        
    def get_about(self):
        about_url = self.site_config['about']
        result = requests.get(about_url).text
        soup = BeautifulSoup(result, 'html.parser')
        dropdown = soup.find('ul', class_='dropmenu-right')
        li_a_href = [li.find('a')['href'] for li in dropdown.find_all('li')]

        about_storage = []

        for href in li_a_href:
            if href.startswith('/p/'):
                result = requests.get(f"https://www.nkust.edu.tw{href}").text
                _inner_soup = BeautifulSoup(result, 'html.parser')
                content = re.sub(r'&#\d+;|&\w+;', '', _inner_soup.find('div', class_="mcont").text.strip())
                breadcrumb = re.sub(r'&#\d+;|&\w+;', '', _inner_soup.find('ol', class_='breadcrumb').text.strip())
                breadcrumb = breadcrumb.replace('\n', '').replace('首頁關於我們','')
                print(f"{breadcrumb}")
                about_storage.append({
                    'title': breadcrumb,
                    'url': f"https://www.nkust.edu.tw{href}",
                    'content': content
                })
            else:
                """
                TODO: 爬取其他關於我們的資訊
                """
                pass
        save_file_name = f'about_{time.strftime("%Y%m%d-%H%M%S")}.json'
        self.write_to_json(save_file_name, about_storage)

        
if __name__ == "__main__":
    nkust = NKUST()
    #nkust.get_hot_news(max_page=1)
    #nkust.get_honors(max_page=1)
    #nkust.get_activity(max_item=10)
    nkust.get_about()
