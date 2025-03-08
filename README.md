# API测试工具

这是一个基于Flask框架的API测试工具，可以方便地配置、保存和执行各种API请求。

## 功能特点

- 添加和管理多个API配置
- 支持GET、POST、PUT、DELETE等HTTP方法
- 可配置查询参数和请求体参数
- 自定义请求头
- 实时执行API请求并显示响应结果
- 保存请求历史记录
- 临时修改参数和请求头

## 安装和运行

### 前提条件

- Python 3.7+
- pip (Python包管理器)

### 安装步骤

1. 克隆或下载本项目到本地

2. 进入项目目录
```
cd api-test-tool
```

3. 安装依赖
```
pip install -r requirements.txt
```

4. 运行应用
```
python app.py
```

5. 在浏览器中访问 http://127.0.0.1:5000

## 使用指南

### 添加API配置

1. 点击首页的"添加新API"按钮
2. 填写API名称、URL和请求方法
3. 添加请求头（JSON格式）
4. 添加参数（可选）
5. 点击"保存配置"按钮

### 执行API请求

1. 在首页点击左侧的API配置
2. 查看和修改默认参数值（可选）
3. 添加临时参数或请求头（可选）
4. 点击"执行请求"按钮
5. 查看响应结果

### 管理API配置

- 点击"编辑"按钮可以修改API配置
- 点击"删除"按钮可以删除API配置
- 点击"历史记录"按钮可以查看请求历史

## 项目结构

```
api-test-tool/
├── app.py              # 主应用文件
├── requirements.txt    # 依赖包列表
├── instance/           # 数据库目录
│   └── api_test.db     # SQLite数据库文件
├── static/             # 静态文件
│   ├── style.css       # 自定义样式
│   └── script.js       # 自定义脚本
└── templates/          # HTML模板
    ├── base.html       # 基础模板
    ├── index.html      # 首页模板
    └── config_form.html # 配置表单模板
```

## 技术栈

- Flask: Web框架
- SQLite: 数据库
- Bootstrap 5: 前端框架
- jQuery: JavaScript库
- Font Awesome: 图标库
- Requests: HTTP客户端库

## 许可证

Apache-2.0 
