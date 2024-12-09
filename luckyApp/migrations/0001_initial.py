# Generated by Django 5.1.4 on 2024-12-09 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LotteryHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('draw_num', models.CharField(max_length=20, unique=True, verbose_name='期号')),
                ('red_ball_1', models.IntegerField(verbose_name='红球1')),
                ('red_ball_2', models.IntegerField(verbose_name='红球2')),
                ('red_ball_3', models.IntegerField(verbose_name='红球3')),
                ('red_ball_4', models.IntegerField(verbose_name='红球4')),
                ('red_ball_5', models.IntegerField(verbose_name='红球5')),
                ('red_ball_6', models.IntegerField(verbose_name='红球6')),
                ('blue_ball', models.IntegerField(verbose_name='蓝球')),
                ('draw_date', models.DateField(verbose_name='开奖日期')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '开奖历史',
                'verbose_name_plural': '开奖历史',
                'ordering': ['-draw_num'],
            },
        ),
        migrations.CreateModel(
            name='PredictionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('draw_num', models.CharField(max_length=20, verbose_name='预测期号')),
                ('red_ball_1', models.IntegerField(verbose_name='红球1')),
                ('red_ball_2', models.IntegerField(verbose_name='红球2')),
                ('red_ball_3', models.IntegerField(verbose_name='红球3')),
                ('red_ball_4', models.IntegerField(verbose_name='红球4')),
                ('red_ball_5', models.IntegerField(verbose_name='红球5')),
                ('red_ball_6', models.IntegerField(verbose_name='红球6')),
                ('blue_ball', models.IntegerField(verbose_name='蓝球')),
                ('prediction_type', models.CharField(max_length=20, verbose_name='预测类型')),
                ('is_hit', models.BooleanField(default=False, verbose_name='是否命中')),
                ('hit_count', models.IntegerField(default=0, verbose_name='命中球数')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='预测时间')),
            ],
            options={
                'verbose_name': '预测记录',
                'verbose_name_plural': '预测记录',
                'ordering': ['-created_at'],
            },
        ),
    ]
