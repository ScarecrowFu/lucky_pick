from django.core.management.base import BaseCommand
from luckyApp.crawler import LotteryCrawler
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '更新最新的双色球开奖数据'

    def handle(self, *args, **options):
        try:
            crawler = LotteryCrawler()
            latest_data = crawler.crawl_latest()
            
            if latest_data:
                self.stdout.write(
                    self.style.SUCCESS(f"成功更新期号 {latest_data['draw_num']} 的开奖数据")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("暂无最新数据")
                )
        except Exception as e:
            logger.error(f"更新数据失败: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f"更新数据失败: {str(e)}")