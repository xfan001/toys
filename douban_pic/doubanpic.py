# coding:utf-8

'''download www.douban.com photos and put it into sqlite database or files'''

import requests
import urllib
from lxml import etree
import re
import sys, os, os.path
import sqlite3


#通过人名得到其相册地址列表
def get_album_id(name):
    home_photo_page = 'http://www.douban.com/people/%s/photos' % name
    try:
        r = requests.get(home_photo_page)
    except HttpConnectionError, e:
        print "error %s: %s" % (e.args[0], args[1])
        sys.exit(1)

    search_numbers = re.findall(ur'共(\d+)个', r.text)
    pages = 1
    if len(search_numbers) != 0:
        pages = (int(search_numbers[0]) - 1) / 16 + 1

    album_urls = []
    for i in range(pages):
        if i:
            data = {'start': 16 * i}
            try:
                r = requests.get(
                    home_photo_page, params=data)
            except HttpConnectionError, e:
                pass
        for url in etree.HTML(r.text).xpath('//a[@class="album_photo"]/@href'):
            url = 'http://www.douban.com/photos/album/%s/' % (re.findall(r'(\d+)', url)[0])
            album_urls.append(url)
    return album_urls


class DoubanPicture():
    def __init__(self, album_id, large_first=False):
        self.album_id = album_id
        self.large_first = large_first

    #得到相册里所有照片地址，返回列表
    def get_album_pic_url(self):
        album_url = 'http://www.douban.com/photos/album/%s/' % self.album_id
        headers = {'user-agent': 'Mozilla/5.0'}
        r = requests.get(album_url, headers=headers)
        if r.status_code != requests.codes.ok:
            print 'requests error!'
            sys.exit(1)
        album_info = etree.HTML(r.text).xpath('//div[@class="wr"]/span[@class="pl"][last()]/text()')[0]
        pic_count = int(re.findall(ur'(\d+)张照片', album_info)[0])
        print 'the numbers of this album: ', pic_count
        all_urls = []
        for i in range((pic_count - 1) / 18 + 1):
            if i:
                try:
                    r = requests.get(album_url, params={'start':18*i}, headers=headers)
                except Exception:
                    continue
            for url in etree.HTML(r.text).xpath('//div[@class="photo_wrap"]/a[@class="photolst_photo"]/@href'):
                photo_id = re.findall(r'(\d+)', url)[0]
                jpg_photo = 'http://img3.douban.com/view/photo/photo/public/p%s.jpg' % photo_id
                if self.large_first:
                    photo_page = 'http://www.douban.com/photos/photo/%s/' % photo_id
                    try:
                        r_photo_page = requests.get(photo_page, headers=headers)
                        html = etree.HTML(r_photo_page.text)
                        jpg_large_list = html.xpath('//div[@class="report-link"]/a/@href')
                        jpg_large = len(jpg_large_list) and jpg_large_list[0] or None
                    except Exception:
                        jpg_large = None
                    jpg_photo = jpg_large or jpg_photo
                all_urls.append(jpg_photo)
        return all_urls


    #insert pictures into table "DouBanPic_table" in 'database'
    def store_photos_database(self, database, album_id, urls):
        with sqlite3.connect(database) as conn:
            conn.text_factory = str
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            if not ('DouBanPic_table',) in cur.fetchall():
                cur.execute("CREATE TABLE DouBanPic_table(AlbumId integer, PhotoUrl text, Data BLOB)")
            for i, url in enumerate(urls):
                print str(i+1) + " writing picture: " + url,
                try:
                    r = requests.get(url, stream=True)
                except Exception, e:
                    print 'error'
                    continue
                data = r.raw.read()
                cur.execute("INSERT INTO DouBanPic_table VALUES (?, ?, ?)", (album_id, url, data))
                print 'done'
    
    
    def store_photos_files(self, dirname, urls):
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        for i, url in enumerate(urls):
            photo_id = re.findall(r'(p\d+)', url)[0]
            filename = os.path.join(dirname, photo_id+'.jpg')
            urllib.urlretrieve(url, filename)
            print '%s/%s, %s' % (i+1, len(urls), url)
            

album_id = 22370378
album_obj = DoubanPicture(album_id, large_first=False)
urls = album_obj.get_album_pic_url()
for i, item in enumerate(urls):
    print i+1, item
album_obj.store_photos_files('test', urls)