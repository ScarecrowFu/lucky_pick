import numpy as np
from datetime import datetime
from .models import LotteryHistory, PredictionRecord
import random
import logging

logger = logging.getLogger(__name__)

class LotteryPredictor:
    def __init__(self):
        self.red_range = range(1, 34)  # 红球范围1-33
        self.blue_range = range(1, 17)  # 蓝球范围1-16

    def generate_random_numbers(self):
        """生成随机号码"""
        red_balls = sorted(random.sample(list(self.red_range), 6))
        blue_ball = random.choice(list(self.blue_range))
        return red_balls, blue_ball

    def get_historical_data(self):
        """获取历史数据"""
        return LotteryHistory.objects.all().order_by('-draw_num')

    def calculate_frequency(self, data):
        """计算号码频率"""
        red_freq = {i: 0 for i in self.red_range}
        blue_freq = {i: 0 for i in self.blue_range}
        
        for record in data:
            red_balls = [
                record.red_ball_1, record.red_ball_2, record.red_ball_3,
                record.red_ball_4, record.red_ball_5, record.red_ball_6
            ]
            for ball in red_balls:
                red_freq[ball] += 1
            blue_freq[record.blue_ball] += 1
            
        return red_freq, blue_freq

    def predict_based_on_frequency(self, num_predictions=5):
        """基于频率预测号码"""
        history_data = self.get_historical_data()[:100]  # 只取最近100期
        if not history_data:
            return []
            
        red_freq, blue_freq = self.calculate_frequency(history_data)
        
        # 转换频率为概率
        total_red = sum(red_freq.values())
        total_blue = sum(blue_freq.values())
        
        red_prob = {k: v/total_red for k, v in red_freq.items()}
        blue_prob = {k: v/total_blue for k, v in blue_freq.items()}
        
        predictions = []
        
        for _ in range(num_predictions):
            # 根据概率选择红球
            red_balls = []
            remaining_red_prob = red_prob.copy()
            
            while len(red_balls) < 6:
                # 归一化剩余概率
                total = sum(remaining_red_prob.values())
                norm_prob = {k: v/total for k, v in remaining_red_prob.items()}
                
                # 选择一个球
                ball = int(np.random.choice(
                    list(norm_prob.keys()),
                    p=list(norm_prob.values())
                ))
                red_balls.append(ball)
                del remaining_red_prob[ball]
            
            red_balls.sort()
            
            # 选择蓝球
            blue_ball = int(np.random.choice(
                list(blue_prob.keys()),
                p=list(blue_prob.values())
            ))
            
            predictions.append({
                'red_balls': red_balls,
                'blue_ball': blue_ball
            })
            
        return predictions

    def check_prediction_accuracy(self, draw_num):
        """检查预测准确性"""
        try:
            actual = LotteryHistory.objects.get(draw_num=draw_num)
            predictions = PredictionRecord.objects.filter(draw_num=draw_num)
            
            actual_red = {
                actual.red_ball_1, actual.red_ball_2, actual.red_ball_3,
                actual.red_ball_4, actual.red_ball_5, actual.red_ball_6
            }
            
            for pred in predictions:
                pred_red = {
                    pred.red_ball_1, pred.red_ball_2, pred.red_ball_3,
                    pred.red_ball_4, pred.red_ball_5, pred.red_ball_6
                }
                
                # 计算命中数
                red_hits = len(actual_red & pred_red)
                blue_hit = actual.blue_ball == pred.blue_ball
                
                # 根据双色球规则判定中奖等级
                prize_level = self._get_prize_level(red_hits, blue_hit)
                
                # 更新预测记录
                pred.hit_count = red_hits + 1 if blue_hit else red_hits  # +1 是为了在模板中方便计算红球命中数
                pred.blue_hit = blue_hit
                pred.is_hit = (prize_level is not None)  # 只要中了任意奖项就算命中
                pred.save()
                
                logger.info(
                    f"期号 {draw_num} 的预测分析结果: "
                    f"红球命中 {red_hits} 个, "
                    f"蓝球{'命中' if blue_hit else '未命中'}, "
                    f"中奖等级: {f'{prize_level}等奖' if prize_level else '未中奖'}"
                )
                
        except LotteryHistory.DoesNotExist:
            logger.warning(f"期号 {draw_num} 的开奖记录不存在")
        except Exception as e:
            logger.error(f"检查预测准确性时发生错误: {str(e)}")

    def _get_prize_level(self, red_hits, blue_hit):
        """
        根据双色球规则判定中奖等级
        返回值：1-6表示对应等级奖项，None表示未中奖
        """
        if red_hits == 6 and blue_hit == 1:
            return 1  # 一等奖：6红+1蓝
        elif red_hits == 6 and blue_hit == 0:
            return 2  # 二等奖：6红+0蓝
        elif red_hits == 5 and blue_hit == 1:
            return 3  # 三等奖：5红+1蓝
        elif (red_hits == 5 and blue_hit == 0) or (red_hits == 4 and blue_hit == 1):
            return 4  # 四等奖：5红+0蓝 或 4红+1蓝
        elif (red_hits == 4 and blue_hit == 0) or (red_hits == 3 and blue_hit == 1):
            return 5  # 五等奖：4红+0蓝 或 3红+1蓝
        elif (red_hits <= 2 and blue_hit == 1):
            return 6  # 六等奖：2红+1蓝 或 1红+1蓝 或 0红+1蓝
        else:
            return None  # 未中奖