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
    
    # 获��新期号
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
    predictor = LotteryPredictor()
    predictions = predictor.predict_based_on_frequency(num_predictions=5)
    
    # 获取最新期号
    latest_record = LotteryHistory.objects.all().order_by('-draw_num').first()
    next_draw_num = str(int(latest_record.draw_num) + 1) if latest_record else "未知"
    
    return JsonResponse({
        'predictions': predictions,
        'draw_num': next_draw_num
    })

@require_http_methods(["POST"])
def save_prediction(request):
    """保存预测号码"""
    try:
        data = json.loads(request.body)
        draw_num = data.get('draw_num')
        red_balls = data.get('red_balls')
        blue_ball = data.get('blue_ball')
        prediction_type = data.get('prediction_type')
        
        if not all([draw_num, red_balls, blue_ball, prediction_type]) or len(red_balls) != 6:
            return JsonResponse({
                'status': 'error',
                'message': '数据格式不正确'
            }, status=400)
            
        # 对红球进行排序，确保比较时顺序一致
        red_balls = sorted(red_balls)
            
        # 检查是否已经存在相同的预测
        existing = PredictionRecord.objects.filter(
            draw_num=draw_num,
            prediction_type=prediction_type
        )
        
        # 检查是否有完全相同的号码组合
        for record in existing:
            record_red_balls = sorted([
                record.red_ball_1, record.red_ball_2, record.red_ball_3,
                record.red_ball_4, record.red_ball_5, record.red_ball_6
            ])
            if (record_red_balls == red_balls and 
                record.blue_ball == blue_ball):
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
    
    # 获取最新期号
    latest_record = LotteryHistory.objects.all().order_by('-draw_num').first()
    latest_draw_num = latest_record.draw_num if latest_record else "0"
    
    # 构建预测记录HTML
    predictions_html = []
    for pred in page_obj:
        status_html = ""
        if str(pred.draw_num) > latest_draw_num:
            status_html = '<span class="badge bg-info">待开奖</span>'
        else:
            if pred.is_hit:
                status_html = '<span class="badge bg-success">命中</span>'
            else:
                status_html = f'''
                    <div>
                        <span class="badge bg-secondary">未中奖</span>
                        <small class="text-muted ms-2">
                            红球: {pred.hit_count} 个
                            , 蓝球: {'1' if pred.blue_hit else '0'} 个
                            ({pred.hit_count}+{'1' if pred.blue_hit else '0'})
                        </small>
                    </div>
                '''
                
        pred_type = "随机选号" if pred.prediction_type == 'random' else "智能预测"
        
        row_html = f"""
        <tr>
            <td>{pred.draw_num}</td>
            <td>
                <span class="lottery-ball red-ball">{pred.red_ball_1}</span>
                <span class="lottery-ball red-ball">{pred.red_ball_2}</span>
                <span class="lottery-ball red-ball">{pred.red_ball_3}</span>
                <span class="lottery-ball red-ball">{pred.red_ball_4}</span>
                <span class="lottery-ball red-ball">{pred.red_ball_5}</span>
                <span class="lottery-ball red-ball">{pred.red_ball_6}</span>
                <span class="lottery-ball blue-ball">{pred.blue_ball}</span>
            </td>
            <td>{pred_type}</td>
            <td>{pred.created_at.strftime('%Y-%m-%d %H:%M')}</td>
            <td>{status_html}</td>
        </tr>
        """
        predictions_html.append(row_html)
    
    # 构建分页HTML
    pagination_html = []
    if page_obj.has_previous():
        pagination_html.append(f'<li class="page-item"><a class="page-link" href="?page=1">&laquo; 首页</a></li>')
        pagination_html.append(f'<li class="page-item"><a class="page-link" href="?page={page_obj.previous_page_number()}">上一页</a></li>')
    
    pagination_html.append(f'<li class="page-item active"><span class="page-link">{page_obj.number} / {page_obj.paginator.num_pages}</span></li>')
    
    if page_obj.has_next():
        pagination_html.append(f'<li class="page-item"><a class="page-link" href="?page={page_obj.next_page_number()}">下一页</a></li>')
        pagination_html.append(f'<li class="page-item"><a class="page-link" href="?page={page_obj.paginator.num_pages}">末页 &raquo;</a></li>')
    
    return JsonResponse({
        'predictions_html': '\n'.join(predictions_html),
        'pagination_html': '\n'.join(pagination_html)
    })