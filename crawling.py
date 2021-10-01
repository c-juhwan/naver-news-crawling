import re
import os
import time
import requests
from pandas import DataFrame
from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm.auto import tqdm


headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"}

def crawling(args):
    print('Start crawling! Keyword: {} Start date: {} End date: {} Exact search: {}'.format(args.search_keyword, args.start_date, args.end_date, args.exact_search))

    driver = webdriver.Chrome(args.webdriver_path)

    if args.start_date is None:
        news_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}'
        news_url = news_url.format(args.search_keyword)
    else:
        news_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}&nso=p%3Afrom{}to{}'
        news_url = news_url.format(args.search_keyword, args.start_date, args.end_date)

    req = requests.get(news_url, headers=headers)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')

    news_dict = {}
    idx = 0
    current_page = 1

    # Article title / press / url
    with tqdm(total = args.max_page, desc='Crawling article title') as pbar:
        while current_page <= args.max_page:
            table = soup.find('ul', {'class' : 'list_news'})
            li_list = table.find_all('li', {'id' : re.compile('sp_nws.*')})
            area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
            a_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]
            info_list = [area.find('div', {'class' : 'info_group'}) for area in area_list]

            for i in range(len(area_list)):
                if args.exact_search:
                    title = a_list[i].get('title')
                    if args.search_keyword not in title:
                        continue # drop the news if the title doesn't contain the query exactly

                # 언론사 URL과 네이버 뉴스 URL 중 후자를 선택
                infos = [info for info in info_list[i].find_all('a')]
                
                if any(press in infos[0].text for press in args.allowed_press):
                    for each_press in args.allowed_press:
                        if each_press in infos[0].text:
                            if '한국경제TV' in infos[0].text or '매일경제TV' in infos[0].text:
                                continue
                            else:
                                press_name = each_press
                                info_naver = infos[1]
                                break
                else:
                    continue

                news_dict[idx] = {}
                news_dict[idx]['title'] = a_list[i].get('title')
                news_dict[idx]['press'] = press_name
                news_dict[idx]['url'] = info_naver.get('href')

                idx += 1

            current_page += 1
            pbar.update(1)

            pages = soup.find('div', {'class' : 'sc_page_inner'})
            for p in pages.find_all('a'):
                if p.text == str(current_page):
                    next_page_url = 'https://search.naver.com/search.naver' + p.get('href')
                    req = requests.get(next_page_url, headers=headers)
                    soup = BeautifulSoup(req.text, 'html.parser')
                    break

    # Article content / publish_date / modify_date / reaction
    for idx in tqdm(range(len(news_dict)), desc='Crawling article content'):
        driver.get(news_dict[idx]['url'])
        time.sleep(3)
        req = requests.get(news_dict[idx]['url'], headers=headers)
        soup = BeautifulSoup(req.text, 'html.parser')
        
        # 기사 내용
        content_div = soup.find('div', {'class' : '_article_body_contents'})
        content = content_div.get_text()
        content = content.replace("\n", "")
        content = content.replace("\t", "")
        content = content.replace("// flash 오류를 우회하기 위한 함수 추가function _flash_removeCallback() {}", "")
        news_dict[idx]['content'] = content

        # 기사 작성/수정 시간
        sponsor_div = soup.find('div', {'class' : 'sponsor'})
        dates = sponsor_div.find_all('span', {'class' : 't11'})

        news_dict[idx]['publish_date'] = dates[0].string
        if len(dates) == 2:
            news_dict[idx]['modify_date'] = dates[1].string

        # 기사 반응
        reaction_good = driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[1]/div/div[2]/div[7]/div[1]/ul/li[1]/a/span[2]').get_attribute('innerHTML')
        reaction_warm = driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[1]/div/div[2]/div[7]/div[1]/ul/li[2]/a/span[2]').get_attribute('innerHTML')
        reaction_sad = driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[1]/div/div[2]/div[7]/div[1]/ul/li[3]/a/span[2]').get_attribute('innerHTML')
        reaction_angry = driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[1]/div/div[2]/div[7]/div[1]/ul/li[4]/a/span[2]').get_attribute('innerHTML')
        reaction_want = driver.find_element_by_xpath('/html/body/div[2]/table/tbody/tr/td[1]/div/div[2]/div[7]/div[1]/ul/li[5]/a/span[2]').get_attribute('innerHTML')

        news_dict[idx]['reaction_good'] = reaction_good
        news_dict[idx]['reaction_warm'] = reaction_warm
        news_dict[idx]['reaction_sad'] = reaction_sad
        news_dict[idx]['reaction_angry'] = reaction_angry
        news_dict[idx]['reaction_want'] = reaction_want

    driver.close()

    # Save data to file
    news_df = DataFrame(news_dict).T
    if args.output_file_path.endswith('.csv'):
        news_df.to_csv(args.output_file_path, encoding='utf-8', index=False)
    elif args.output_file_path.endswith('.xlsx'):
        news_df.to_excel(args.output_file_path, index=False)
    elif args.output_file_path.endswith('.json'):
        news_df.to_json(args.output_file_path, orient='records', force_ascii=False)
    
    print('Done! saved crawling result to {}'.format(args.output_file_path))