import numpy as np
from datetime import datetime
from .models import LotteryHistory, PredictionRecord
import random
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class MultiDimensionalAnalyzer:
    """多维度分析器"""
    def __init__(self):
        self.red_range = range(1, 34)  # 红球范围1-33
        self.blue_range = range(1, 17)  # 蓝球范围1-16
        self.recent_periods = 30  # 最近30期数据用于冷热分析
        self.history_data = None
        self.red_freq = None
        self.blue_freq = None
        # 初始权重
        self.weights = {
            'frequency': 0.30,
            'hot_cold': 0.20,
            'missing': 0.15,
            'interval': 0.15,
            'odd_even': 0.10,
            'zone': 0.10
        }
        # 权重调整参数
        self.weight_adjust_rate = 0.05  # 权重调整步长
        self.min_weight = 0.05  # 最小权重
        self.max_weight = 0.40  # 最大权重
        # 维度得分历史记录
        self.dimension_history = {
            'hot_cold': [],
            'missing': [],
            'interval': [],
            'odd_even': [],
            'zone': []
        }
        # 维度效果评估
        self.dimension_performance = {
            'hot_cold': 0,
            'missing': 0,
            'interval': 0,
            'odd_even': 0,
            'zone': 0
        }

    def load_history_data(self, limit=100):
        """加载历史数据"""
        self.history_data = list(LotteryHistory.objects.all().order_by('-draw_num')[:limit])
        return self.history_data

    def analyze_hot_cold(self):
        """冷热号分析"""
        if not self.history_data:
            self.load_history_data(self.recent_periods)

        # 初始化计数器
        red_count = defaultdict(int)
        blue_count = defaultdict(int)

        # 统计最近30期号码出现次数
        for record in self.history_data[:self.recent_periods]:
            red_balls = [
                record.red_ball_1, record.red_ball_2, record.red_ball_3,
                record.red_ball_4, record.red_ball_5, record.red_ball_6
            ]
            for ball in red_balls:
                red_count[ball] += 1
            blue_count[record.blue_ball] += 1

        # 分类冷热号
        red_hot = []    # 出现>=3次
        red_warm = []   # 出现1-2次
        red_cold = []   # 未出现
        
        for num in self.red_range:
            count = red_count[num]
            if count >= 3:
                red_hot.append(num)
            elif count > 0:
                red_warm.append(num)
            else:
                red_cold.append(num)

        return {
            'red_hot': red_hot,
            'red_warm': red_warm,
            'red_cold': red_cold,
            'red_count': dict(red_count),
            'blue_count': dict(blue_count)
        }

    def analyze_missing_values(self):
        """遗漏值分析"""
        if not self.history_data:
            self.load_history_data()

        # 初始化最后出现期号
        red_last_appear = {i: 0 for i in self.red_range}
        blue_last_appear = {i: 0 for i in self.blue_range}
        
        # 获取最新期号
        latest_draw = int(self.history_data[0].draw_num)
        
        # 分析遗漏值
        for record in self.history_data:
            draw_num = int(record.draw_num)
            red_balls = [
                record.red_ball_1, record.red_ball_2, record.red_ball_3,
                record.red_ball_4, record.red_ball_5, record.red_ball_6
            ]
            
            # 更新红球最后出现期号
            for ball in red_balls:
                if red_last_appear[ball] == 0:
                    red_last_appear[ball] = draw_num
                    
            # 更新蓝球最后出现期号
            if blue_last_appear[record.blue_ball] == 0:
                blue_last_appear[record.blue_ball] = draw_num

        # 计算遗漏值
        red_missing = {num: latest_draw - last_draw if last_draw > 0 else latest_draw 
                      for num, last_draw in red_last_appear.items()}
        blue_missing = {num: latest_draw - last_draw if last_draw > 0 else latest_draw 
                       for num, last_draw in blue_last_appear.items()}

        return {
            'red_missing': red_missing,
            'blue_missing': blue_missing
        }

    def analyze_intervals(self):
        """号码间隔分析"""
        if not self.history_data:
            self.load_history_data()

        intervals = []
        for record in self.history_data:
            red_balls = sorted([
                record.red_ball_1, record.red_ball_2, record.red_ball_3,
                record.red_ball_4, record.red_ball_5, record.red_ball_6
            ])
            # 计算相邻号码间隔
            record_intervals = []
            for i in range(len(red_balls)-1):
                interval = red_balls[i+1] - red_balls[i]
                record_intervals.append(interval)
            intervals.append(record_intervals)

        # 统计间隔出现频率
        interval_freq = defaultdict(int)
        for record_intervals in intervals:
            for interval in record_intervals:
                interval_freq[interval] += 1

        return {
            'interval_freq': dict(interval_freq),
            'avg_intervals': [sum(x)/len(x) for x in intervals]
        }

    def analyze_odd_even(self):
        """奇偶比例分析"""
        if not self.history_data:
            self.load_history_data()

        ratios = []
        for record in self.history_data:
            red_balls = [
                record.red_ball_1, record.red_ball_2, record.red_ball_3,
                record.red_ball_4, record.red_ball_5, record.red_ball_6
            ]
            # 统计奇数个数
            odd_count = sum(1 for x in red_balls if x % 2 == 1)
            even_count = 6 - odd_count
            ratios.append((odd_count, even_count))

        # 统计各种比例出现的次数
        ratio_freq = defaultdict(int)
        for ratio in ratios:
            ratio_freq[ratio] += 1

        return {
            'ratio_freq': dict(ratio_freq),
            'most_common_ratios': sorted(
                ratio_freq.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
        }

    def analyze_zones(self):
        """区间分布分析"""
        if not self.history_data:
            self.load_history_data()

        zone_distributions = []
        for record in self.history_data:
            red_balls = [
                record.red_ball_1, record.red_ball_2, record.red_ball_3,
                record.red_ball_4, record.red_ball_5, record.red_ball_6
            ]
            # 统计红球区间分布
            zone1 = sum(1 for x in red_balls if 1 <= x <= 11)
            zone2 = sum(1 for x in red_balls if 12 <= x <= 22)
            zone3 = sum(1 for x in red_balls if 23 <= x <= 33)
            zone_distributions.append((zone1, zone2, zone3))

        # 统计区间分布频率
        zone_freq = defaultdict(int)
        for dist in zone_distributions:
            zone_freq[dist] += 1

        return {
            'zone_freq': dict(zone_freq),
            'most_common_zones': sorted(
                zone_freq.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
        }

    def analyze_all_dimensions(self):
        """执行所有维度的分析"""
        self.load_history_data()
        
        return {
            'hot_cold': self.analyze_hot_cold(),
            'missing_values': self.analyze_missing_values(),
            'intervals': self.analyze_intervals(),
            'odd_even': self.analyze_odd_even(),
            'zones': self.analyze_zones()
        }

    def score_hot_cold(self, red_balls):
        """评分：冷热号分布"""
        analysis = self.analyze_hot_cold()
        red_hot = set(analysis['red_hot'])
        red_warm = set(analysis['red_warm'])
        red_cold = set(analysis['red_cold'])
        
        # 计算所选号码中热温冷的数量
        hot_count = sum(1 for ball in red_balls if ball in red_hot)
        warm_count = sum(1 for ball in red_balls if ball in red_warm)
        cold_count = sum(1 for ball in red_balls if ball in red_cold)
        
        # 理想比例：2-3个热号，2-3个温号，1个冷号
        hot_score = 100 if 2 <= hot_count <= 3 else 60
        warm_score = 100 if 2 <= warm_count <= 3 else 60
        cold_score = 100 if cold_count == 1 else 60
        
        return (hot_score * 0.4 + warm_score * 0.4 + cold_score * 0.2)

    def score_missing_values(self, red_balls):
        """评分：遗漏值分布"""
        analysis = self.analyze_missing_values()
        red_missing = analysis['red_missing']
        
        # 计算选中号码的遗漏值
        missing_values = [red_missing[ball] for ball in red_balls]
        
        # 评分规则：
        # 1. 至少包含1个遗漏值较大的号码（遗漏值>10）
        # 2. 不要选择太多遗漏值大的号码
        # 3. 遗漏值的分布应该相对均匀
        high_missing = sum(1 for v in missing_values if v > 10)
        max_missing = max(missing_values)
        min_missing = min(missing_values)
        avg_missing = sum(missing_values) / len(missing_values)
        
        # 计算得分
        score = 100
        if high_missing == 0:
            score -= 20  # 没有大遗漏值扣分
        elif high_missing > 2:
            score -= 10  # 大遗漏值太多扣分
            
        if max_missing - min_missing > 20:
            score -= 10  # 遗漏值差距太大扣分
            
        return score

    def score_intervals(self, red_balls):
        """评分：号码间隔"""
        sorted_balls = sorted(red_balls)
        intervals = [sorted_balls[i+1] - sorted_balls[i] for i in range(len(sorted_balls)-1)]
        
        # 获取历史间隔数据
        analysis = self.analyze_intervals()
        interval_freq = analysis['interval_freq']
        
        # 评分规则：
        # 1. 间隔不应该太大（>8）或太小（=1）
        # 2. 间隔应该符合历史频率分布
        # 3. 间隔的分布应该均匀
        score = 100
        
        # 检查间隔是否合理
        for interval in intervals:
            if interval > 8:
                score -= 10
            elif interval == 1:
                score -= 5
                
        # 检查间隔的频率分布
        for interval in intervals:
            freq = interval_freq.get(interval, 0)
            if freq < 10:  # 历史上很少出现的间隔
                score -= 5
                
        return max(score, 0)

    def score_odd_even(self, red_balls):
        """评分：奇偶比例"""
        odd_count = sum(1 for x in red_balls if x % 2 == 1)
        even_count = 6 - odd_count
        
        analysis = self.analyze_odd_even()
        common_ratios = [ratio for ratio, _ in analysis['most_common_ratios']]
        
        # 评分规则：
        # 1. 奇偶比应该在常见比例中
        # 2. 避免极端比例（6:0或0:6）
        score = 100
        
        if (odd_count, even_count) in common_ratios:
            score = 100
        elif odd_count in [2,3,4]:  # 较为合理的比例
            score = 80
        elif odd_count in [1,5]:    # 不太合理的比例
            score = 60
        else:                       # 极端比例
            score = 40
            
        return score

    def score_zones(self, red_balls):
        """评分：区间分布"""
        # 计算区间分布
        zone1 = sum(1 for x in red_balls if 1 <= x <= 11)
        zone2 = sum(1 for x in red_balls if 12 <= x <= 22)
        zone3 = sum(1 for x in red_balls if 23 <= x <= 33)
        
        analysis = self.analyze_zones()
        common_zones = [dist for dist, _ in analysis['most_common_zones']]
        
        # 评分规则：
        # 1. 区间分布应该在常见分布中
        # 2. 避免号码过于集中
        # 3. 每个区间至少要有1个号码
        score = 100
        
        if (zone1, zone2, zone3) in common_zones:
            score = 100
        elif min(zone1, zone2, zone3) >= 1:  # 每个区间都有号码
            score = 80
        elif max(zone1, zone2, zone3) >= 4:  # 某个区间过于集中
            score = 60
        else:
            score = 40
            
        return score

    def calculate_comprehensive_score(self, red_balls, blue_ball):
        """计算综合得分"""
        scores = {
            'hot_cold': self.score_hot_cold(red_balls),
            'missing': self.score_missing_values(red_balls),
            'interval': self.score_intervals(red_balls),
            'odd_even': self.score_odd_even(red_balls),
            'zone': self.score_zones(red_balls)
        }
        
        # 计算加权总分
        total_score = (
            scores['hot_cold'] * self.weights['hot_cold'] +
            scores['missing'] * self.weights['missing'] +
            scores['interval'] * self.weights['interval'] +
            scores['odd_even'] * self.weights['odd_even'] +
            scores['zone'] * self.weights['zone']
        )
        
        # 返回详细得分和总分
        return {
            'detailed_scores': scores,
            'total_score': total_score,
            'weights': self.weights
        }

    def evaluate_number_combination(self, red_balls, blue_ball):
        """评估号码组合的质量"""
        if len(red_balls) != 6 or not all(1 <= x <= 33 for x in red_balls):
            return {'error': '红球数量必须为6个，且在1-33范围内'}
            
        if not (1 <= blue_ball <= 16):
            return {'error': '蓝球必须在1-16范围内'}
            
        # 确保数据已加载
        if not self.history_data:
            self.load_history_data()
            
        # 计算综合得分
        score_result = self.calculate_comprehensive_score(red_balls, blue_ball)
        
        # 添加评估建议
        suggestions = []
        detailed_scores = score_result['detailed_scores']
        
        if detailed_scores['hot_cold'] < 70:
            suggestions.append('建议调整冷热号的比例')
        if detailed_scores['missing'] < 70:
            suggestions.append('建议考虑遗漏值的分布')
        if detailed_scores['interval'] < 70:
            suggestions.append('建议优化号码间隔')
        if detailed_scores['odd_even'] < 70:
            suggestions.append('建议调整奇偶比例')
        if detailed_scores['zone'] < 70:
            suggestions.append('建议优化区间分布')
            
        score_result['suggestions'] = suggestions
        return score_result

    def update_dimension_history(self, scores, is_hit):
        """更新维度历史记录"""
        for dimension, score in scores.items():
            if len(self.dimension_history[dimension]) >= 50:
                self.dimension_history[dimension].pop(0)
            self.dimension_history[dimension].append({
                'score': score,
                'is_hit': is_hit
            })

    def evaluate_dimension_performance(self):
        """评估各维度的表现"""
        for dimension in self.dimension_performance:
            history = self.dimension_history[dimension]
            if not history:
                continue
                
            # 计算维度的效果得分
            hit_scores = [h['score'] for h in history if h['is_hit']]
            miss_scores = [h['score'] for h in history if not h['is_hit']]
            
            # 如果命中的平均分高于未命中的平均分，说明这个维度的判断较准确
            hit_avg = sum(hit_scores) / len(hit_scores) if hit_scores else 0
            miss_avg = sum(miss_scores) / len(miss_scores) if miss_scores else 0
            
            # 计算维度效果（命中平均分与未命中平均分的差值）
            self.dimension_performance[dimension] = hit_avg - miss_avg

    def adjust_weights(self):
        """调整权重"""
        if not any(self.dimension_history.values()):
            return  # 如果没有历史数据，不调整权重
            
        # 评估维度表现
        self.evaluate_dimension_performance()
        
        # 计算性能得分的总和（用于归一化）
        total_performance = sum(abs(score) for score in self.dimension_performance.values())
        if total_performance == 0:
            return
            
        # 根据性能得分调整权重
        new_weights = {}
        for dimension, performance in self.dimension_performance.items():
            # 计算权重调整量
            adjustment = (performance / total_performance) * self.weight_adjust_rate
            current_weight = self.weights[dimension]
            
            # 应用调整，确保在限制范围内
            new_weight = max(self.min_weight, min(self.max_weight, current_weight + adjustment))
            new_weights[dimension] = new_weight
            
        # 归一化新权重，确保总和为1
        total_weight = sum(new_weights.values())
        for dimension in new_weights:
            new_weights[dimension] /= total_weight
            
        # 更新权重
        self.weights.update(new_weights)
        
        logger.info("权重已更新: %s", self.weights)

    def record_prediction_result(self, prediction_scores, is_hit):
        """记录预测结果并更新权重"""
        # 更新历史记录
        self.update_dimension_history(prediction_scores, is_hit)
        
        # 当累积足够的历史数据时调整权重
        if len(next(iter(self.dimension_history.values()))) >= 10:
            self.adjust_weights()

class LotteryPredictor:
    def __init__(self):
        self.red_range = range(1, 34)  # 红球范围1-33
        self.blue_range = range(1, 17)  # 蓝球范围1-16
        self.analyzer = MultiDimensionalAnalyzer()  # 创建分析器实例
        self.min_score_threshold = 75  # 最低接受分数

    def generate_random_numbers(self):
        """生成随机号码"""
        red_balls = sorted(random.sample(list(self.red_range), 6))
        blue_ball = random.choice(list(self.blue_range))
        return red_balls, blue_ball

    def predict_based_on_frequency(self, num_predictions=5):
        """基于频率和多维度分析预测号码"""
        predictions = []
        max_attempts = 100  # 最大尝试次数
        attempts = 0
        
        while len(predictions) < num_predictions and attempts < max_attempts:
            # 生成候选号码
            candidate = self._generate_candidate_numbers()
            red_balls, blue_ball = candidate['numbers']
            score_result = candidate['score_result']
            
            # 如果分数达到阈值，加入预测结果
            if score_result['total_score'] >= self.min_score_threshold:
                predictions.append({
                    'red_balls': red_balls,
                    'blue_ball': blue_ball,
                    'score': score_result['total_score'],
                    'analysis': score_result
                })
            
            attempts += 1
            
        # 如果达到最大尝试次数仍未生成足够的预测，降低标准重试
        if len(predictions) < num_predictions:
            self.min_score_threshold = 60  # 降低分数阈值
            while len(predictions) < num_predictions:
                candidate = self._generate_candidate_numbers()
                red_balls, blue_ball = candidate['numbers']
                predictions.append({
                    'red_balls': red_balls,
                    'blue_ball': blue_ball,
                    'score': 60,
                    'analysis': {'total_score': 60}
                })
        
        # 按分数排序，返回最好的num_predictions个结果
        predictions.sort(key=lambda x: x['score'], reverse=True)
        return predictions[:num_predictions]

    def _generate_candidate_numbers(self):
        """生成候选号码并评分"""
        # 获取分析数据
        analysis = self.analyzer.analyze_all_dimensions()
        
        # 根据冷热号分析选择红球
        hot_cold = analysis['hot_cold']
        red_balls = self._select_red_balls_with_strategy(hot_cold)
        
        # 选择蓝球
        blue_ball = self._select_blue_ball_with_strategy(analysis)
        
        # 评估号码组合
        score_result = self.analyzer.evaluate_number_combination(red_balls, blue_ball)
        
        return {
            'numbers': (red_balls, blue_ball),
            'score_result': score_result
        }

    def _select_red_balls_with_strategy(self, hot_cold_analysis):
        """根据策略选择红球"""
        red_hot = hot_cold_analysis['red_hot']
        red_warm = hot_cold_analysis['red_warm']
        red_cold = hot_cold_analysis['red_cold']
        
        # 按照40%热号、40%温号、20%冷号的比例选择
        selected = []
        
        # 选择2-3个热号
        hot_count = random.randint(2, 3)
        if red_hot:
            selected.extend(random.sample(red_hot, min(hot_count, len(red_hot))))
        
        # 选择2-3个温号
        warm_count = 3 if hot_count == 2 else 2
        if red_warm:
            selected.extend(random.sample(red_warm, min(warm_count, len(red_warm))))
        
        # 补充冷号
        cold_count = 6 - len(selected)
        if cold_count > 0 and red_cold:
            selected.extend(random.sample(red_cold, min(cold_count, len(red_cold))))
        
        # 如果号码不足6个，从所有号码中随机补充
        while len(selected) < 6:
            remaining = list(set(range(1, 34)) - set(selected))
            selected.append(random.choice(remaining))
        
        return sorted(selected)

    def _select_blue_ball_with_strategy(self, analysis):
        """根据策略选择蓝球"""
        # 获取蓝球分析数据
        blue_missing = analysis['missing_values']['blue_missing']
        
        # 根据遗漏值计算权重
        weights = {}
        for ball in self.blue_range:
            missing = blue_missing.get(ball, 0)
            # 漏值越大，权重越高，但有上限
            weight = min(missing / 10, 2.0) if missing > 0 else 0.5
            weights[ball] = weight
        
        # 归一化权重
        total_weight = sum(weights.values())
        for ball in weights:
            weights[ball] /= total_weight
        
        # 按权重随机选择
        return int(np.random.choice(
            list(weights.keys()),
            p=list(weights.values())
        ))

    def check_prediction_accuracy(self, draw_num):
        """检查预测准确性并更新权重"""
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
                
                # 判定中奖等级
                prize_level = self._get_prize_level(red_hits, blue_hit)
                is_hit = prize_level is not None
                
                # 重新评估这组号码
                red_balls = sorted(list(pred_red))
                score_result = self.analyzer.evaluate_number_combination(red_balls, pred.blue_ball)
                
                # 记录预测结果并更新权重
                self.analyzer.record_prediction_result(score_result['detailed_scores'], is_hit)
                
                # 更新预测记录
                pred.hit_count = red_hits
                pred.blue_hit = blue_hit
                pred.is_hit = is_hit
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
        if red_hits == 6 and blue_hit:
            return 1  # 一等奖：6红+1蓝
        elif red_hits == 6 and not blue_hit:
            return 2  # 二等奖：6红+0蓝
        elif red_hits == 5 and blue_hit:
            return 3  # 三等奖：5红+1蓝
        elif (red_hits == 5 and not blue_hit) or (red_hits == 4 and blue_hit):
            return 4  # 四等奖：5红+0蓝 或 4红+1蓝
        elif (red_hits == 4 and not blue_hit) or (red_hits == 3 and blue_hit):
            return 5  # 五等奖：4红+0蓝 或 3红+1蓝
        elif red_hits <= 2 and blue_hit:
            return 6  # 六等奖：2红+1蓝 或 1红+1蓝 或 0红+1蓝
        else:
            return None  # 未中奖