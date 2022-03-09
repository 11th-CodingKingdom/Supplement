from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

# client = MongoClient('mongodb://test:test@54.144.213.113:27017')
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

def melonCrawling(rank_type, region, year):
    driver.get('https://www.melon.com/chart/age/index.htm?chartType='+rank_type+'&chartGenre='+region+'&chartDate='+str(year))
    chart = driver.page_source
    soup = BeautifulSoup(chart, 'html.parser')
    datas = soup.select('#frm > table > tbody > tr')
    for music in datas:
        albumID = music.select_one('td:nth-child(3) > div > a > span').get('onclick').strip("javascript:melon.link.goAlbumDetail ('").strip("');")
        songID = music.select_one('td:nth-child(1) > div > input').get('value')
        title = music.select_one('td:nth-child(4) > div > div > div.ellipsis.rank01 > span').text.strip(' \n')
        rank = music.select_one('td:nth-child(2) > div > span').text
        singer = music.select_one('td:nth-child(4) > div > div > div:nth-child(3) > div.ellipsis.rank02 > span').text
        like = music.select_one('td:nth-child(5) > div > button > span.cnt').text.strip(' \n').strip('총건수\n')
        albumImageUrl = music.select_one('td:nth-child(3) > div > a > img').get('src')
        musics = {'albumID':albumID,'songID':songID, 'Region': region, 'year': year, 'rank_type' : rank_type, 'rank': rank, 'title': title, 'singer': singer, 'like': int(like.replace(",", "")),'albumImageUrl':albumImageUrl}
        db.musics.insert_one(musics)
        print(songID +"/"+ albumID)

def albumUrlCrawling():
    music_list = db.musics.find({},{'_id':False})
    for i in music_list:
        songID = i['songID']
        driver.get('https://www.melon.com/song/detail.htm?songId='+songID)
        chart = driver.page_source
        soup = BeautifulSoup(chart, 'html.parser')
        albumImageUrl = soup.select_one('#downloadfrm > div > div > div.thumb > a > img').get('src')
        genre = soup.select_one('#downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(6)').text
        db.musics.update_one({'songID':songID}, {"$set":{"genre":genre}})
        db.musics.update_one({'songID':songID}, {"$set": {"albumImageUrl": albumImageUrl}})
        print(str(j) + "%" + songID + "%" + genre + "%" + albumImageUrl)

def insert_all():
    db.musics.drop()
    Region = ['KPOP']
    rank_type = ['AG', 'YE']
    for g in Region:
        for t in rank_type :
            i = 1980
            while i < 2020:
                melonCrawling(t, g, i)
                if t == 'AG':
                    i += 10
                else :
                    i += 1
    albumUrlCrawling()

insert_all()