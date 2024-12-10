from django.core.management.base import BaseCommand
from django.utils import timezone
from luckyApp.models import LotteryHistory
from luckyApp.crawler import LotteryCrawler
from luckyApp.predictor import LotteryPredictor
import logging
import time
import random

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '定时任务管理器：自动更新开奖数据和分析命中情况'

    def add_arguments(self, parser):
        # 创建互斥参数组
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--daemon',
            action='store_true',
            help='以守护进程模式运行，定期检查更新'
        )
        group.add_argument(
            '--test',
            action='store_true',
            help='测试模式：生成测试数据并触发分析'
        )
        group.add_argument(
            '--init',
            action='store_true',
            help='初始化模式：抓取所有历史数据'
        )

    def handle(self, *args, **options):
        if options['test']:
            self.stdout.write('启动测试模式...')
            self.run_test()
            return
            
        if options['init']:
            self.stdout.write('启动初始化模式...')
            self.run_init()
            return
            
        self.stdout.write('启动定时任务管理器...')
        
        while True:
            try:
                self.check_and_update()
                
                if not options['daemon']:
                    break
                    
                # 每10分钟检查一次
                time.sleep(600)
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('定时任务管理器已停止'))
                break
            except Exception as e:
                logger.error(f"定时任务执行出错: {str(e)}")
                if not options['daemon']:
                    raise
                time.sleep(300)  # 发生错误后等待5分钟再试

    def run_init(self):
        """运行初始化模式"""
        try:
            # 检查是否已有数据
            if LotteryHistory.objects.exists():
                self.stdout.write(
                    self.style.WARNING('数据库中已有数据，确认要重新初始化吗？[y/N]')
                )
                confirm = input().lower()
                if confirm != 'y':
                    self.stdout.write('初始化已取消')
                    return
                    
                # 清空现有数据
                self.stdout.write('清空现有数据...')
                LotteryHistory.objects.all().delete()
            
            # 开始抓取历史数据
            self.stdout.write('开始抓取历史数据...')
            crawler = LotteryCrawler()
            crawler.crawl_history()
            
            # 获取数据统计
            total_records = LotteryHistory.objects.count()
            latest_record = LotteryHistory.objects.order_by('-draw_num').first()
            earliest_record = LotteryHistory.objects.order_by('draw_num').first()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n初始化完成！\n"
                    f"总计抓取: {total_records} 期\n"
                    f"数据范围: {earliest_record.draw_num} - {latest_record.draw_num}\n"
                    f"时间范围: {earliest_record.draw_date} - {latest_record.draw_date}"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"初始化过程中发生错误: {str(e)}")
            )

    def run_test(self):
        """运行测试模式"""
        try:
            # 1. 获取最新记录
            latest_record = LotteryHistory.objects.order_by('-draw_num').first()
            if not latest_record:
                self.stdout.write('数据库为空，无法进行测试')
                return
                
            # 2. 生成新一期的期号
            next_draw_num = str(int(latest_record.draw_num) + 1)
            
            # 3. 生成随机开奖号码
            red_balls = sorted(random.sample(range(1, 34), 6))
            blue_ball = random.randint(1, 16)
            
            # 4. 创建新的开奖记录
            # new_record = LotteryHistory.objects.create(
            #     draw_num=next_draw_num,
            #     red_ball_1=red_balls[0],
            #     red_ball_2=red_balls[1],
            #     red_ball_3=red_balls[2],
            #     red_ball_4=red_balls[3],
            #     red_ball_5=red_balls[4],
            #     red_ball_6=red_balls[5],
            #     blue_ball=blue_ball,
            #     draw_date=timezone.now().date()
            # )
            # 测试
            new_record = LotteryHistory.objects.create(
                draw_num=next_draw_num,
                red_ball_1=6,
                red_ball_2=11,
                red_ball_3=12,
                red_ball_4=21,
                red_ball_5=red_balls[4],
                red_ball_6=red_balls[5],
                blue_ball=7,
                draw_date=timezone.now().date()
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"已生成测试数据 期号:{next_draw_num}\n"
                    f"红球: {red_balls}\n"
                    f"蓝球: {blue_ball}"
                )
            )
            
            # 5. 触发命中分析
            predictor = LotteryPredictor()
            predictor.check_prediction_accuracy(next_draw_num)
            
            self.stdout.write(self.style.SUCCESS('测试完成'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"测试过程中发生错误: {str(e)}")
            )

    def check_and_update(self):
        """检查并更新数据"""
        # 1. 获取最新记录
        latest_record = LotteryHistory.objects.order_by('-draw_num').first()
        
        # 2. 爬取最新数据
        crawler = LotteryCrawler()
        latest_data = crawler.crawl_latest()
        
        if not latest_data:
            self.stdout.write('未获取到最新数据')
            return
            
        if not latest_record or latest_data['draw_num'] > latest_record.draw_num:
            self.stdout.write(f'发现新数据：期号 {latest_data["draw_num"]}')
            # 分析命中情况
            predictor = LotteryPredictor()
            predictor.check_prediction_accuracy(latest_data['draw_num'])
        else:
            self.stdout.write('数据已是最新')