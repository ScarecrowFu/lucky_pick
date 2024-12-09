from django.core.management.base import BaseCommand
from luckyApp.crawler import LotteryCrawler
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '爬取双色球历史开奖数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-year',
            type=int,
            default=2003,
            help='起始年份'
        )
        parser.add_argument(
            '--end-year',
            type=int,
            default=None,
            help='结束年份'
        )
        parser.add_argument(
            '--latest',
            action='store_true',
            help='只爬取最新一期数据'
        )

    def handle(self, *args, **options):
        try:
            crawler = LotteryCrawler()
            
            if options['latest']:
                self.stdout.write('开始爬取最新一期数据...')
                latest_data = crawler.crawl_latest()
                if latest_data:
                    self.stdout.write(
                        self.style.SUCCESS(f"成功爬取期号 {latest_data['draw_num']} 的开奖数据")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("未获取到最新数据")
                    )
            else:
                start_year = options['start_year']
                end_year = options['end_year'] or datetime.now().year
                self.stdout.write(f'开始爬取 {start_year} 到 {end_year} 年的数据...')
                crawler.crawl_history(start_year)
                self.stdout.write(
                    self.style.SUCCESS('数据爬取完成')
                )
        except Exception as e:
            logger.error(f"爬取数据失败: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f"爬取数据失败: {str(e)}")
            ) 