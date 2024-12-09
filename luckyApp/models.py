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
    draw_num = models.CharField(max_length=20, verbose_name='预测期��')
    red_ball_1 = models.IntegerField(verbose_name='红球1')
    red_ball_2 = models.IntegerField(verbose_name='红球2')
    red_ball_3 = models.IntegerField(verbose_name='红球3')
    red_ball_4 = models.IntegerField(verbose_name='红球4')
    red_ball_5 = models.IntegerField(verbose_name='红球5')
    red_ball_6 = models.IntegerField(verbose_name='红球6')
    blue_ball = models.IntegerField(verbose_name='蓝球')
    prediction_type = models.CharField(max_length=20, verbose_name='预测类型')  # random/analysis
    is_hit = models.BooleanField(default=False, verbose_name='是否命中')
    hit_count = models.IntegerField(default=0, verbose_name='命中球数')
    blue_hit = models.BooleanField(default=False, verbose_name='蓝球是否命中')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='预测时间')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '预测记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.draw_num} - {self.prediction_type}"
