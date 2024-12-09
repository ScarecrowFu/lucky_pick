import requests, bs4
import os, time
import operator
from itertools import combinations, permutations
 
 
 
class DoubleColorBall(object):
    def __init__(self):
        self.balls = {}
        self.baseUrl = 'http://tubiao.zhcw.com/tubiao/ssqNew/ssqJsp/ssqZongHeFengBuTuAsc.jsp'
        self.dataFile = './balls_data3.txt'
 
    def getHtml(self, url):
        headers = {
            'Referer': 'http://tubiao.zhcw.com/tubiao/ssqNew/ssqInc/ssqZongHeFengBuTuAsckj_year=2016.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        self.session = requests.Session()
        response = self.session.get(url, headers=headers)
        return response.text
 
    def getBall(self):
        for year in range(2003, 2022):
            url = self.baseUrl + '?kj_year=%s' % (year,)
            print(url)
            html = self.getHtml(url)
            self.bs = bs4.BeautifulSoup(html, 'html.parser')
            if self.bs:
                data = self.bs.find_all(class_='hgt')
                self.parseBall(data)
 
    def parseBall(self, data):
        self.balls = {}
        for row in data:
            if not isinstance(row, bs4.element.Tag):
                continue
            center = row.find(class_="qh7").string.strip()
            print(center)
            if center.startswith("模拟"):
                break
            redBalls = row.find_all(class_="redqiu")
            blueBall = row.find(class_="blueqiu3").string.strip()
            self.balls[center] = [r.string for r in redBalls] + [blueBall]
 
        self.saveBall(self.balls)
 
    def saveBall(self, data):
        with open(self.dataFile, 'a+') as f:
            for r in sorted(data, reverse=False):  #降序
            # for r in sorted(data, reverse=True):  #升序
                f.write(str(r) + ' ' + ' '.join(data[r]) + '\n')
 
 
if __name__ == '__main__':
    ball = DoubleColorBall()
    ball.getBall()