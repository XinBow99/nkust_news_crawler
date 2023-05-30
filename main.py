import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import json
import time

class NKUST:
    def __init__(self) -> None:
        self.host = f"https://www.nkust.edu.tw/p/"
        self.lang = "zh-tw"

        self.site_config = {
            "hot_news": f"{self.host}403-1000-1363-page.php?Lang={self.lang}",
            "honors": f"{self.host}403-1000-13-page.php?Lang={self.lang}",
            "activity" : f"https://ws1.nkust.edu.tw/Activity/#",
        }
    
    def get_target_news_url(self, news_type, max_page=-1):
        target_url = self.site_config[news_type]
        first_page = requests.get(target_url.replace('page','1'))
        soup = BeautifulSoup(first_page.text, 'html.parser')
        # Get the last page number
        last_page = soup.find('span', class_='pg-txt').text
        last_page = int(re.findall(r'\d+', last_page)[0]) if max_page == -1 else max_page
        
        total_news_url = []



        for page_num in tqdm(range(1, last_page+1)):
            page_url = target_url.replace('page', str(page_num))
            page = requests.get(page_url)
            soup = BeautifulSoup(page.text, 'html.parser')
            news_list = soup.find_all('div', class_='listBS')
            tqdm.write(f"Page {page_num} has {len(news_list)} news")
            for news in news_list:
                title = news.find('div', class_='mtitle')
                href = title.find('a')['href']
                total_news_url.append(href)
        tqdm.write(f"Total {len(total_news_url)} news")
        return total_news_url
    
    def get_target_news_content(self, news_url):
        html_content = requests.get(news_url).text
        # 創建BeautifulSoup對象，指定解析器為lxml
        soup = BeautifulSoup(html_content, 'html.parser')

        # 提取標題信息
        title = soup.find('h2', class_='hdline').text.strip()
        mcont = soup.find('div', class_='mcont')
        ptinfoproperty_date = mcont.find('span', class_='ptinfoproperty_date')
        ptinfoproperty_date = '' if ptinfoproperty_date is None else ptinfoproperty_date.find('span').text.strip()
        mcont_p = mcont.find_all('p')
        content = ''
        for p in mcont_p:
            content += p.text.strip()
        return {
            'title': title,
            'url': news_url,
            'date': ptinfoproperty_date,
            'content': content
        }

    def get_hot_news(self, max_page=-1):
        """
        爬取焦點新聞，以下是相關參數
        max_page: -1 means all pages, else means the number of pages
        """
        hot_news_url = self.get_target_news_url('hot_news', max_page)
        news_storage = []
        for url in tqdm(hot_news_url, desc='hot_news'):
            result = self.get_target_news_content(url)
            news_storage.append(result)
            tqdm.write(f"{result['date']} {result['title']}")
        save_file_name = f'hot_news_{time.strftime("%Y%m%d-%H%M%S")}.json'
        with open(save_file_name, 'w', encoding='utf-8') as f:
            json.dump(news_storage, f, ensure_ascii=False, indent=4)
            print(f'{save_file_name} saved')
    
    def get_honors(self, max_page=-1):
        """
        爬取榮譽榜，以下是相關參數
        max_page: -1 means all pages, else means the number of pages
        """
        honors_url = self.get_target_news_url('honors', max_page)
        news_storage = []
        for url in tqdm(honors_url, desc='honors'):
            result = self.get_target_news_content(url)
            news_storage.append(result)
            tqdm.write(f"{result['date']} {result['title']}")
        save_file_name = f'honors_{time.strftime("%Y%m%d-%H%M%S")}.json'
        with open(save_file_name, 'w', encoding='utf-8') as f:
            json.dump(news_storage, f, ensure_ascii=False, indent=4)
            print(f'{save_file_name} saved')
    
    def get_activity(self):
        activity_url = self.site_config['activity']
        # <a class="justify-content-center" href="/Activity/Home/Event?Sno=20230221172739Ro9ws6">
        Snos = re.findall(r'Sno=(.*)"', requests.get(activity_url).text)
        # 去除重複
        Snos = list(set(Snos))
        news_storage = []
        for Sno in tqdm(Snos, desc='activity'):
            _url = f"https://ws1.nkust.edu.tw/Activity/Home/Event?Sno={Sno}"
            result = requests.get(_url).text
            # get h2 title
            title = re.findall(r'<h2>(.*)</h2>', result)[0]
            # 清除特殊字元 &#128266;&#128266;
            title = re.sub(r'&#\d+;', '', title)
            title = re.sub(r'&\w+;', '', title)
            
            # get content
            soup = BeautifulSoup(result, 'html.parser')
            content = soup.find('div', class_='blog-main').text.strip()
            content = re.sub(r'&#\d+;', '', content)
            content = re.sub(r'&\w+;', '', content)

            tqdm.write(f"{title}")
            
            news_storage.append({
                'title': title,
                'url': _url,
                'content': content
            })
        with open(f'activity_{time.strftime("%Y%m%d-%H%M%S")}.json', 'w', encoding='utf-8') as f:
            json.dump(news_storage, f, ensure_ascii=False, indent=4)
            print(f'activity_{time.strftime("%Y%m%d-%H%M%S")}.json saved')
        
if __name__ == "__main__":
    nkust = NKUST()
    nkust.get_hot_news()
    nkust.get_honors()
    nkust.get_activity()