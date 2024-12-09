import requests
import bs4
from datetime import datetime
from .models import LotteryHistory
import logging

logger = logging.getLogger(__name__)

class LotteryCrawler:
    def __init__(self):
        self.base_url = 'http://tubiao.zhcw.com/tubiao/ssqNew/ssqJsp/ssqZongHeFengBuTuAsc.jsp'
        self.headers = {
            'Referer': 'http://tubiao.zhcw.com/tubiao/ssqNew/ssqInc/ssqZongHeFengBuTuAsckj_year=2016.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        self.session = requests.Session()

    def get_html(self, url):
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"获取页面失败: {str(e)}")
            return None

    def parse_data(self, data):
        results = []
        for row in data:
            if not isinstance(row, bs4.element.Tag):
                continue
            
            center = row.find(class_="qh7").string.strip()
            if center.startswith("模拟"):
                break
                
            red_balls = [int(r.string) for r in row.find_all(class_="redqiu")]
            blue_ball = int(row.find(class_="blueqiu3").string.strip())
            
            # 获取日期
            date_link = row.find(class_="qh7").find('a')
            if date_link and date_link.get('title'):
                date_str = date_link.get('title').split('：')[-1]
                try:
                    draw_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    draw_date = datetime.now().date()
            else:
                draw_date = datetime.now().date()
            
            results.append({
                'draw_num': center,
                'red_balls': red_balls,
                'blue_ball': blue_ball,
                'draw_date': draw_date
            })
            
        return results

    def save_to_db(self, lottery_data):
        if not isinstance(lottery_data, list):
            lottery_data = [lottery_data]
            
        for data in lottery_data:
            try:
                LotteryHistory.objects.update_or_create(
                    draw_num=data['draw_num'],
                    defaults={
                        'red_ball_1': data['red_balls'][0],
                        'red_ball_2': data['red_balls'][1],
                        'red_ball_3': data['red_balls'][2],
                        'red_ball_4': data['red_balls'][3],
                        'red_ball_5': data['red_balls'][4],
                        'red_ball_6': data['red_balls'][5],
                        'blue_ball': data['blue_ball'],
                        'draw_date': data['draw_date']
                    }
                )
                logger.info(f"已保存期号 {data['draw_num']} 的数据")
            except Exception as e:
                logger.error(f"保存期号 {data['draw_num']} 的数据失败: {str(e)}")

    def crawl_history(self, start_year=2003):
        """爬取历史数据"""
        current_year = datetime.now().year
        for year in range(start_year, current_year + 1):
            url = f"{self.base_url}?kj_year={year}"
            logger.info(f"正在爬取 {year} 年的数据")
            html = self.get_html(url)
            if html:
                bs = bs4.BeautifulSoup(html, 'html.parser')
                if bs:
                    data = bs.find_all(class_='hgt')
                    lottery_data = self.parse_data(data)
                    if lottery_data:
                        self.save_to_db(lottery_data)
                        logger.info(f"已完成{year}年数据爬取")

    def crawl_latest(self):
        """爬取最新一期数据"""
        current_year = datetime.now().year
        url = f"{self.base_url}?kj_year={current_year}"
        html = self.get_html(url)
        if html:
            bs = bs4.BeautifulSoup(html, 'html.parser')
            if bs:
                data = bs.find_all(class_='hgt')
                if data:
                    # 获取最后一行数据（最新一期）
                    valid_data = [row for row in data if isinstance(row, bs4.element.Tag) and not row.find(class_="qh7").string.strip().startswith("模拟")]
                    if valid_data:
                        latest_data = self.parse_data([valid_data[-1]])
                        if latest_data:
                            self.save_to_db(latest_data[0])
                            return latest_data[0]
        return None

    def crawl_specific(self, draw_num):
        """爬取指定期号的数据"""
        # 获取年份
        year = '20' + draw_num[:2]
        url = f"{self.base_url}?kj_year={year}"
        html = self.get_html(url)
        
        if html:
            bs = bs4.BeautifulSoup(html, 'html.parser')
            if bs:
                data = bs.find_all(class_='hgt')
                lottery_data = self.parse_data(data)
                if lottery_data:
                    # 找到指定期号的数据
                    target_data = None
                    for item in lottery_data:
                        if item['draw_num'] == draw_num:
                            target_data = item
                            break
                    
                    if target_data:
                        self.save_to_db([target_data])
                        logger.info(f"成功补充期号 {draw_num} 的数据")
                        return target_data
                    
        logger.warning(f"未找到期号 {draw_num} 的数据")
        return None