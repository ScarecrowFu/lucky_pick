from django.db import models
from django.utils import timezone

class LotteryHistory(models.Model):
    """双色球历史开奖记录"""
    draw_num = models.CharField(max_length=20, unique=True, verbose_name='期号')
    red_ball_1 = models.IntegerField(verbose_name='红球1')
    red_ball_2 = models.IntegerField(verbose_name='红球2')
    red_ball_3 = models.IntegerField(verbose_name='红球3')
    red_ball_4 = models.IntegerField(verbose_name='红球4')
    red_ball_5 = models.IntegerField(verbose_name='红球5')
    red_ball_6 = models.IntegerField(verbose_name='红球6')
    blue_ball = models.IntegerField(verbose_name='蓝球')
    draw_date = models.DateField(verbose_name='开奖日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        ordering = ['-draw_num']
        verbose_name = '开奖历史'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.draw_num} - {self.draw_date}"

class PredictionRecord(models.Model):
    """预测记录"""
    PREDICTION_TYPES = [
        ('random', '随机选号'),
        ('analysis', '智能分析'),
    ]
    
    draw_num = models.CharField(max_length=20, verbose_name='预测期号')
    red_ball_1 = models.IntegerField(verbose_name='红球1')
    red_ball_2 = models.IntegerField(verbose_name='红球2')
    red_ball_3 = models.IntegerField(verbose_name='红球3')
    red_ball_4 = models.IntegerField(verbose_name='红球4')
    red_ball_5 = models.IntegerField(verbose_name='红球5')
    red_ball_6 = models.IntegerField(verbose_name='红球6')
    blue_ball = models.IntegerField(verbose_name='蓝球')
    prediction_type = models.CharField(
        max_length=20, 
        choices=PREDICTION_TYPES,
        verbose_name='预测类型'
    )
    is_hit = models.BooleanField(default=False, verbose_name='是否命中')
    hit_count = models.IntegerField(default=0, verbose_name='命中球数')
    blue_hit = models.BooleanField(default=False, verbose_name='蓝球是否命中')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='预测时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '预测记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.draw_num} - {self.get_prediction_type_display()}"

    @property
    def is_drawn(self):
        """判断该期是否已开奖"""
        try:
            latest_history = LotteryHistory.objects.latest('draw_num')
            return int(self.draw_num) <= int(latest_history.draw_num)
        except LotteryHistory.DoesNotExist:
            return False

    @property
    def hit_prize_level(self):
        """获取中奖等级"""
        if not self.is_hit:
            return None
        
        if self.hit_count == 6 and self.blue_hit:
            return 1
        elif self.hit_count == 6:
            return 2
        elif self.hit_count == 5 and self.blue_hit:
            return 3
        elif self.hit_count == 5 or (self.hit_count == 4 and self.blue_hit):
            return 4
        elif self.hit_count == 4 or (self.hit_count == 3 and self.blue_hit):
            return 5
        elif self.blue_hit:
            return 6
        return None
