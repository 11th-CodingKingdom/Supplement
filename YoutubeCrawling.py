from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.retroMusic

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('headless')
options.add_argument("disable-gpu")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWeb Kit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 검색하여 동영상 재생 url 찾기
def youtubeCrawling(songID, singer,title, search_text):
    # driver로 특정 페이지를 크롤링한다.
    url = 'https://www.youtube.com/results?search_query='+search_text
    driver.get(url)
    chart = driver.page_source
    soup = BeautifulSoup(chart, 'html.parser')
    musicPlaySrc = 'https://www.youtube.com/embed'+soup.select_one('#video-title').get('href').replace('watch?v=', '')
    informations = {'songID': songID, 'title': title, 'singer': singer, 'musicPlaySrc': musicPlaySrc}
    db.musicPlaySrc.insert_one(informations)
    print(musicPlaySrc)

def insert_all():
    # db.musicPlaySrc.drop()
    music_list = db.musics.find({},{'_id':False})
    print(music_list)
    j = 0
    for i in music_list:
        songID = i['songID']
        title = i['title']
        singer = i['singer']
        search_text = (i['title'].replace(" ", '+') + "+" + i['singer'].replace(" ", '+'))
        print(str(j) + "%" + search_text)
        youtubeCrawling(songID, singer,title, search_text)
        j += 1

insert_all()