# Preparation:
#   Python environment must have BeautifulSoup, requests and lxml installed, see cmds
#   source venv/bin/activate
#   pip install beautifulsoup4 requests lxml
#   python3 get_play_cnt_delta.py  to run
import requests
import random  # build-in in Python
import re
from   bs4 import BeautifulSoup

# Used to contain both songs and bonus data
videos = []

headers = {    # Latest User Agent https://www.whatismybrowser.com/guides/the-latest-user-agent/chrome
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
}

#! Find total number of pages for songs or bonuses from the last paginator box, 1 is first paginated page
def find_num_of_pages(category, server):
    # category is either 'All' or 'Bonus'. 1 is first paginated page number
    if server == 'linode':
        baseurl = 'https://www.chinesesong.net'
    elif server == 'local':
        baseurl = 'http://localhost:5001'
    else:
        print("Error: server must be linode or local")
        return None, None

    response = requests.get(baseurl + f'/songs/{category}/1', headers=headers)  # e.g, https://chinesesong.net/songs/All/1

    soup           = BeautifulSoup(response.content, 'lxml')   # 'lxml': For parsing HTML and XML doc.
    all_page_boxes = soup.find_all('a', class_ = 'btn')
    last_page_box  = all_page_boxes[-1] if all_page_boxes else None
    last_page      = int(last_page_box.text.strip())
    return baseurl, last_page


#! Visit baseurl + '/songs/All/x' or baseurl + '/songs/Bonus/x' (where x=1,2,3...last_page)
# to get the html pages for all the paginated songs or bonuses to get song titles and play counters
# category is either "song" or "bonus"
def get_data_from_server(category, server):
    baseurl, last_page = find_num_of_pages(category, server)  #! Call function defined above
    if last_page == -1:
        return -1

    # print(f'Scraping {baseurl} from page 1 ~ {last_page} to get play counter deltas for {category}...')

    for page in range(1, last_page + 1):
        response = requests.get(f'{baseurl}/songs/{category}/{page}', headers=headers)
        soup     = BeautifulSoup(response.content, 'lxml')     # Parse the response

        songs    = soup.find_all('article', class_ = 'media content_section')
        for song in songs:
            play_cnt = song.find('span', class_='cnt')
            # Use find instead of find_all to skip bonuses,  href=True ensures return only tags that
            # have an href attributes. Iterating over a tag gives you its text node(s) directly when
            # the tag contains only simple text. Actually .text below is not necessary
            a_tag = song.find('a', href=True)
            song_title = a_tag.text.strip()
            song_url   = a_tag['href']
            # Replace song/<song_id> with selenium/<song_id>
            slnm_url = re.sub(r"song/(\d+)", r"selenium/\1", song_url)
            url        = (baseurl + f'{slnm_url}')
            videos.append({"title": song_title, "url": url})
    return 0
