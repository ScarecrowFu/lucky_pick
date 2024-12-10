from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import LotteryHistory, PredictionRecord
from .crawler import LotteryCrawler
from .predictor import LotteryPredictor
from django.core.paginator import Paginator
import json

@ensure_csrf_cookie
def index(request):
    """首页视图"""
    # 获取最新的开奖记录
    latest_records = LotteryHistory.objects.all().order_by('-draw_num')[:1]
    
    # 获取最新的预测记录
    latest_predictions = PredictionRecord.objects.filter(
        prediction_type='analysis'
    ).order_by('-created_at')[:1]
    
    # 获取统计数据
    total_records = LotteryHistory.objects.count()
    total_predictions = PredictionRecord.objects.count()
    hit_predictions = PredictionRecord.objects.filter(is_hit=True).count()
    hit_rate = round((hit_predictions / total_predictions * 100) if total_predictions > 0 else 0, 1)
    
    context = {
        'latest_records': latest_records,
        'latest_predictions': latest_predictions,
        'total_records': total_records,
        'hit_rate': hit_rate,
    }
    return render(request, 'luckyApp/index.html', context)

@ensure_csrf_cookie
@require_http_methods(["GET"])
def history_list(request):
    """历史开奖记录列表"""
    page = request.GET.get('page', 1)
    records = LotteryHistory.objects.all().order_by('-draw_num')
    paginator = Paginator(records, 20)
    page_obj = paginator.get_page(page)
    
    return render(request, 'luckyApp/history.html', {'page_obj': page_obj})

@ensure_csrf_cookie
@require_http_methods(["GET"])
def prediction_list(request):
    """预测记录列表"""
    page = request.GET.get('page', 1)
    predictions = PredictionRecord.objects.all().order_by('-created_at')
    paginator = Paginator(predictions, 20)
    page_obj = paginator.get_page(page)
    
    # 获取最新期号
    latest_record = LotteryHistory.objects.all().order_by('-draw_num').first()
    latest_draw_num = latest_record.draw_num if latest_record else "0"
    
    context = {
        'page_obj': page_obj,
        'latest_draw_num': latest_draw_num
    }
    return render(request, 'luckyApp/predictions.html', context)

@require_http_methods(["POST"])
def generate_random(request):
    """生成随机号码"""
    predictor = LotteryPredictor()
    
    # 获取最新期号
    latest_record = LotteryHistory.objects.all().order_by('-draw_num').first()
    next_draw_num = str(int(latest_record.draw_num) + 1) if latest_record else "未知"
    
    # 生成5组随机号码
    result = []
    for _ in range(5):
        red_balls, blue_ball = predictor.generate_random_numbers()
        result.append({
            'red_balls': red_balls,
            'blue_ball': blue_ball
        })
    
    return JsonResponse({
        'predictions': result,
        'draw_num': next_draw_num
    })

@require_http_methods(["POST"])
def generate_prediction(request):
    """生成智能预测号码"""
    try:
        predictor = LotteryPredictor()
        predictions = predictor.predict_based_on_frequency(num_predictions=5)
        
        # 获取最新期号
        latest_record = LotteryHistory.objects.all().order_by('-draw_num').first()
        next_draw_num = str(int(latest_record.draw_num) + 1) if latest_record else "未知"
        
        # 确保返回格式正确
        formatted_predictions = []
        for pred in predictions:
            formatted_predictions.append({
                'red_balls': pred['red_balls'],
                'blue_ball': pred['blue_ball'],
                'score': pred.get('score', 0),
                'analysis': pred.get('analysis', {})
            })
        
        return JsonResponse({
            'status': 'success',
            'predictions': formatted_predictions,
            'draw_num': next_draw_num,
            'message': '预测生成成功'
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 打印详细错误信息
        return JsonResponse({
            'status': 'error',
            'message': f'生成预测失败: {str(e)}'
        }, status=500)

@require_http_methods(["POST"])
def save_prediction(request):
    """保存预测号码"""
    try:
        data = json.loads(request.body)
        draw_num = data.get('draw_num')
        red_balls = data.get('red_balls')
        blue_ball = data.get('blue_ball')
        prediction_type = data.get('prediction_type')
        
        if not all([draw_num, red_balls, blue_ball is not None, prediction_type]) or len(red_balls) != 6:
            return JsonResponse({
                'status': 'error',
                'message': '数据格式不正确'
            }, status=400)
            
        # 对红球进行排序，确保比较时顺序一致
        red_balls = sorted(red_balls)
            
        # 检查是否已经存在相同的预测
        existing = PredictionRecord.objects.filter(
            draw_num=draw_num,
            red_ball_1=red_balls[0],
            red_ball_2=red_balls[1],
            red_ball_3=red_balls[2],
            red_ball_4=red_balls[3],
            red_ball_5=red_balls[4],
            red_ball_6=red_balls[5],
            blue_ball=blue_ball,
            prediction_type=prediction_type
        ).exists()
        
        if existing:
            return JsonResponse({
                'status': 'error',
                'message': '该预测号码已经记录过了'
            }, status=400)
            
        # 保存预测记录
        PredictionRecord.objects.create(
            draw_num=draw_num,
            red_ball_1=red_balls[0],
            red_ball_2=red_balls[1],
            red_ball_3=red_balls[2],
            red_ball_4=red_balls[3],
            red_ball_5=red_balls[4],
            red_ball_6=red_balls[5],
            blue_ball=blue_ball,
            prediction_type=prediction_type,
            hit_count=0,  # 初始化命中数为0
            is_hit=False,  # 初始化未命中
            blue_hit=False  # 初始化蓝球未命中
        )
        
        return JsonResponse({
            'status': 'success',
            'message': '预测号码已保存'
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 打印详细错误信息
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["POST"])
def update_lottery_data(request):
    """更新最新开奖数据"""
    crawler = LotteryCrawler()
    latest_data = crawler.crawl_latest()
    
    if latest_data:
        # 检查预测准确性
        predictor = LotteryPredictor()
        predictor.check_prediction_accuracy(latest_data['draw_num'])
        
        return JsonResponse({
            'status': 'success',
            'message': f"成功更新期号 {latest_data['draw_num']} 的开奖数据"
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': "暂无最新数据"
        })

@require_http_methods(["GET"])
def get_latest_predictions(request):
    """获取最新预测记录"""
    page = request.GET.get('page', 1)
    predictions = PredictionRecord.objects.all().order_by('-created_at')
    paginator = Paginator(predictions, 20)
    page_obj = paginator.get_page(page)
    
    # 构建预测记录HTML
    predictions_html = []
    for pred in page_obj:
        # 构建移动端和PC端共用的HTML
        row_html = f'''
            <tr class="prediction-row">
                <!-- 移动端显示 -->
                <td class="d-md-none">
                    <div class="prediction-mobile-view">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="text-primary">期号：{pred.draw_num}</span>
                            {f'<span class="badge bg-success">命中{pred.hit_prize_level}等奖</span>' if pred.is_hit else
                             '<span class="badge bg-secondary">未中奖</span>' if pred.is_drawn else
                             '<span class="badge bg-warning text-dark">待开奖</span>'}
                        </div>
                        <div class="lottery-numbers mb-2">
                            <span class="lottery-ball red-ball">{pred.red_ball_1}</span>
                            <span class="lottery-ball red-ball">{pred.red_ball_2}</span>
                            <span class="lottery-ball red-ball">{pred.red_ball_3}</span>
                            <span class="lottery-ball red-ball">{pred.red_ball_4}</span>
                            <span class="lottery-ball red-ball">{pred.red_ball_5}</span>
                            <span class="lottery-ball red-ball">{pred.red_ball_6}</span>
                            <span class="lottery-ball blue-ball">{pred.blue_ball}</span>
                        </div>
                        <div class="prediction-info">
                            <small class="text-muted">
                                {pred.get_prediction_type_display()} | 
                                {pred.created_at.strftime('%Y-%m-%d %H:%M')}
                            </small>
                        </div>
                    </div>
                </td>

                <!-- PC端显示 -->
                <td class="d-none d-md-table-cell">{pred.draw_num}</td>
                <td class="d-none d-md-table-cell">
                    <div class="lottery-numbers">
                        <span class="lottery-ball red-ball">{pred.red_ball_1}</span>
                        <span class="lottery-ball red-ball">{pred.red_ball_2}</span>
                        <span class="lottery-ball red-ball">{pred.red_ball_3}</span>
                        <span class="lottery-ball red-ball">{pred.red_ball_4}</span>
                        <span class="lottery-ball red-ball">{pred.red_ball_5}</span>
                        <span class="lottery-ball red-ball">{pred.red_ball_6}</span>
                        <span class="lottery-ball blue-ball">{pred.blue_ball}</span>
                    </div>
                </td>
                <td class="d-none d-md-table-cell">{pred.get_prediction_type_display()}</td>
                <td class="d-none d-md-table-cell">{pred.created_at.strftime('%Y-%m-%d %H:%M')}</td>
                <td class="d-none d-md-table-cell">
                    {f'<span class="badge bg-success">命中{pred.hit_prize_level}等奖</span>' if pred.is_hit else
                     '<span class="badge bg-secondary">未中奖</span>' if pred.is_drawn else
                     '<span class="badge bg-warning text-dark">待开奖</span>'}
                </td>
            </tr>
        '''
        predictions_html.append(row_html)
    
    # 如果没有记录，显示空状态
    if not predictions_html:
        predictions_html.append('<tr><td colspan="5" class="text-center">暂无记录</td></tr>')
    
    # 构建分页HTML
    pagination_html = []
    if page_obj.has_previous():
        pagination_html.extend([
            '<li class="page-item">',
            f'<a class="page-link" href="?page=1">&laquo; 首页</a>',
            '</li>',
            '<li class="page-item">',
            f'<a class="page-link" href="?page={page_obj.previous_page_number()}">上一页</a>',
            '</li>'
        ])
    
    pagination_html.extend([
        '<li class="page-item active">',
        f'<span class="page-link">{page_obj.number} / {page_obj.paginator.num_pages}</span>',
        '</li>'
    ])
    
    if page_obj.has_next():
        pagination_html.extend([
            '<li class="page-item">',
            f'<a class="page-link" href="?page={page_obj.next_page_number()}">下一页</a>',
            '</li>',
            '<li class="page-item">',
            f'<a class="page-link" href="?page={page_obj.paginator.num_pages}">末页 &raquo;</a>',
            '</li>'
        ])
    
    return JsonResponse({
        'predictions_html': ''.join(predictions_html),
        'pagination_html': ''.join(pagination_html)
    })
