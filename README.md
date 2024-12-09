# 双色球智能预测系统

这是一个基于Django开发的双色球智能预测系统，通过分析历史数据，提供智能预测和随机选号功能。

## 功能特性

- **数据采集**
  - 自动抓取最新开奖数据
  - 支持历史数据批量导入
  - 实时更新开奖信息

- **智能预测**
  - 基于历史数据的频率分析
  - 支持多组号码同时预测
  - 预测结果可保存追踪

- **随机选号**
  - 提供随机选号功能
  - 支持多组号码生成
  - 选号结果可保存记录

- **数据分析**
  - 显示历史开奖记录
  - 预测号码命中统计
  - 中奖等级判定
  - 详细的命中情况展示

## 技术栈

- Python 3.8+
- Django 5.1
- Bootstrap 5
- MySQL
- HTML5/CSS3
- JavaScript/Ajax

## 安装说明

1. **克隆项目**
```bash
git clone [项目地址]
cd luckyPick
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
python manage.py migrate
```

5. **导入历史数据**
```bash
python manage.py lottery_scheduler --init
```

## 启动项目

1. **启动开发服务器**
```bash
python manage.py runserver
```

2. **访问系统**
打开浏览器访问 http://127.0.0.1:8000

## 定时任务

系统包含以下定时任务：

1. **数据更新任务**
- 自动更新最新开奖数据
- 建议通过cron或计划任务定期执行

2. **预测分析任务**
- 用于测试预测效果
- 可选择性执行

## 项目结构

```
luckyPick/
├── luckyApp/                 # 主应用目录
│   ├── management/          # 管理命令
│   ├── migrations/          # 数据库迁移
│   ├── templates/          # 模板文件
│   ├── models.py           # 数据模型
│   ├── views.py            # 视图函数
│   ├── urls.py             # URL配置
│   ├── crawler.py          # 数据爬虫
│   └── predictor.py        # 预测逻辑
├── luckyPick/              # 项目配置
├── static/                 # 静态文件
├── manage.py              # 管理脚本
└── requirements.txt       # 项目依赖
```

## 使用说明

1. **智能预测**
   - 点击"智能��析"进入预测页面
   - 系统会生成多组预测号码
   - 可以选择保存感兴趣的号码组合

2. **随机选号**
   - 点击"随机选号"生成随机号码
   - 支持多组号码同时生成
   - 可以保存选中的号码

3. **历史记录**
   - 查看历史开奖数据
   - 追踪预测号码的命中情况
   - 显示详细的中奖统计

## 注意事项

- 系统预测结果仅供参考，不构成购彩建议
- 建议定期执行数据更新任务保持数据最新
- 请合理使用爬虫功能，避免频繁请求
- 建议在生产环境中使用更可靠的数据库（如MySQL）

## 开发计划

- [ ] 添加更多预测算法
- [ ] 优化数据分析展示
- [ ] 增加用户管理功能
- [ ] 支持自定义预测参数
- [ ] 添加数据导出功能

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

MIT License 