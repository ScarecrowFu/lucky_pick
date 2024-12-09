from django.core.management.base import BaseCommand
from luckyApp.models import LotteryHistory, PredictionRecord
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = '创建测试数据以展示不同的命中情况'

    def handle(self, *args, **options):
        # 清理已有的测试数据
        self.stdout.write('清理已有数据...')
        LotteryHistory.objects.all().delete()
        PredictionRecord.objects.all().delete()

        # 创建一些历史开奖记录
        self.stdout.write('创建历史开奖记录...')
        
        # 第23140期 - 用于测试完全命中
        LotteryHistory.objects.create(
            draw_num='23140',
            red_ball_1=1, red_ball_2=2, red_ball_3=3,
            red_ball_4=4, red_ball_5=5, red_ball_6=6,
            blue_ball=7,
            draw_date=datetime.now().date() - timedelta(days=14)
        )
        
        # 第23141期 - 用于测试部分命中
        LotteryHistory.objects.create(
            draw_num='23141',
            red_ball_1=1, red_ball_2=2, red_ball_3=13,
            red_ball_4=14, red_ball_5=15, red_ball_6=16,
            blue_ball=7,
            draw_date=datetime.now().date() - timedelta(days=7)
        )
        
        # 第23142期 - 用于测试未命中
        LotteryHistory.objects.create(
            draw_num='23142',
            red_ball_1=11, red_ball_2=12, red_ball_3=13,
            red_ball_4=14, red_ball_5=15, red_ball_6=16,
            blue_ball=16,
            draw_date=datetime.now().date()
        )

        self.stdout.write('创建预测记录...')
        
        # 1. 完全命中的预测 (命中5个号码)
        PredictionRecord.objects.create(
            draw_num='23140',
            red_ball_1=1, red_ball_2=2, red_ball_3=3,
            red_ball_4=4, red_ball_5=5, red_ball_6=16,
            blue_ball=7,
            prediction_type='analysis',
            created_at=datetime.now() - timedelta(days=15),
            hit_count=5,
            is_hit=True
        )
        
        # 2. 部分命中的预测 (命中2个号码)
        PredictionRecord.objects.create(
            draw_num='23141',
            red_ball_1=1, red_ball_2=2, red_ball_3=23,
            red_ball_4=24, red_ball_5=25, red_ball_6=26,
            blue_ball=16,
            prediction_type='random',
            created_at=datetime.now() - timedelta(days=8),
            hit_count=2,
            is_hit=False
        )
        
        # 3. 未命中的预测
        PredictionRecord.objects.create(
            draw_num='23142',
            red_ball_1=1, red_ball_2=2, red_ball_3=3,
            red_ball_4=4, red_ball_5=5, red_ball_6=6,
            blue_ball=7,
            prediction_type='analysis',
            created_at=datetime.now() - timedelta(days=1),
            hit_count=0,
            is_hit=False
        )
        
        # 4. 待开奖的预测
        PredictionRecord.objects.create(
            draw_num='23143',
            red_ball_1=1, red_ball_2=2, red_ball_3=3,
            red_ball_4=4, red_ball_5=5, red_ball_6=6,
            blue_ball=7,
            prediction_type='random',
            created_at=datetime.now(),
            hit_count=0,
            is_hit=False
        )

        self.stdout.write(self.style.SUCCESS('测试数据创建完成！'))
        self.stdout.write('你现在可以在网页上查看不同的命中情况：')
        self.stdout.write('1. 完全命中 (23140期 - 命中5个号码)')
        self.stdout.write('2. 部分命中 (23141期 - 命中2个号码)')
        self.stdout.write('3. 未命中 (23142期)')
        self.stdout.write('4. 待开奖 (23143期)') 