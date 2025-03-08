from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import requests
import json
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'api_test_tool_secret_key'

# 添加上下文处理器，为所有模板提供当前时间
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# 确保数据库目录存在
if not os.path.exists('instance'):
    os.makedirs('instance')

# 初始化数据库
def init_db():
    conn = sqlite3.connect('instance/api_test.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        method TEXT NOT NULL,
        headers TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_id INTEGER,
        param_name TEXT NOT NULL,
        param_value TEXT,
        param_type TEXT NOT NULL,
        FOREIGN KEY (config_id) REFERENCES api_configs (id) ON DELETE CASCADE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        config_id INTEGER,
        request_data TEXT,
        response_data TEXT,
        status_code INTEGER,
        execution_time REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (config_id) REFERENCES api_configs (id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# 首页 - 显示所有API配置
@app.route('/')
def index():
    conn = sqlite3.connect('instance/api_test.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM api_configs ORDER BY created_at DESC')
    configs = cursor.fetchall()
    conn.close()
    return render_template('index.html', configs=configs)

# 添加新的API配置页面
@app.route('/config/new', methods=['GET'])
def new_config():
    return render_template('config_form.html', config=None, params=[])

# 保存API配置
@app.route('/config/save', methods=['POST'])
def save_config():
    name = request.form.get('name')
    url = request.form.get('url')
    method = request.form.get('method')
    headers = request.form.get('headers', '{}')
    
    # 验证必填字段
    if not name or not url or not method:
        flash('名称、URL和方法为必填项', 'danger')
        return redirect(url_for('new_config'))
    
    conn = sqlite3.connect('instance/api_test.db')
    cursor = conn.cursor()
    
    # 保存API配置
    cursor.execute(
        'INSERT INTO api_configs (name, url, method, headers) VALUES (?, ?, ?, ?)',
        (name, url, method, headers)
    )
    config_id = cursor.lastrowid
    
    # 保存参数
    param_names = request.form.getlist('param_name[]')
    param_values = request.form.getlist('param_value[]')
    param_types = request.form.getlist('param_type[]')
    
    for i in range(len(param_names)):
        if param_names[i]:  # 只保存有名称的参数
            cursor.execute(
                'INSERT INTO api_params (config_id, param_name, param_value, param_type) VALUES (?, ?, ?, ?)',
                (config_id, param_names[i], param_values[i] if i < len(param_values) else '', 
                 param_types[i] if i < len(param_types) else 'query')
            )
    
    conn.commit()
    conn.close()
    
    flash('API配置已成功保存', 'success')
    return redirect(url_for('index'))

# 编辑API配置
@app.route('/config/edit/<int:config_id>', methods=['GET'])
def edit_config(config_id):
    conn = sqlite3.connect('instance/api_test.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取配置信息
    cursor.execute('SELECT * FROM api_configs WHERE id = ?', (config_id,))
    config = cursor.fetchone()
    
    # 获取参数信息
    cursor.execute('SELECT * FROM api_params WHERE config_id = ?', (config_id,))
    params = cursor.fetchall()
    
    conn.close()
    
    if not config:
        flash('未找到API配置', 'danger')
        return redirect(url_for('index'))
    
    return render_template('config_form.html', config=config, params=params)

# 更新API配置
@app.route('/config/update/<int:config_id>', methods=['POST'])
def update_config(config_id):
    name = request.form.get('name')
    url = request.form.get('url')
    method = request.form.get('method')
    headers = request.form.get('headers', '{}')
    
    # 验证必填字段
    if not name or not url or not method:
        flash('名称、URL和方法为必填项', 'danger')
        return redirect(url_for('edit_config', config_id=config_id))
    
    conn = sqlite3.connect('instance/api_test.db')
    cursor = conn.cursor()
    
    # 更新API配置
    cursor.execute(
        'UPDATE api_configs SET name = ?, url = ?, method = ?, headers = ? WHERE id = ?',
        (name, url, method, headers, config_id)
    )
    
    # 删除旧参数
    cursor.execute('DELETE FROM api_params WHERE config_id = ?', (config_id,))
    
    # 保存新参数
    param_names = request.form.getlist('param_name[]')
    param_values = request.form.getlist('param_value[]')
    param_types = request.form.getlist('param_type[]')
    
    for i in range(len(param_names)):
        if param_names[i]:  # 只保存有名称的参数
            cursor.execute(
                'INSERT INTO api_params (config_id, param_name, param_value, param_type) VALUES (?, ?, ?, ?)',
                (config_id, param_names[i], param_values[i] if i < len(param_values) else '', 
                 param_types[i] if i < len(param_types) else 'query')
            )
    
    conn.commit()
    conn.close()
    
    flash('API配置已成功更新', 'success')
    return redirect(url_for('index'))

# 删除API配置
@app.route('/config/delete/<int:config_id>', methods=['POST'])
def delete_config(config_id):
    conn = sqlite3.connect('instance/api_test.db')
    cursor = conn.cursor()
    
    # 删除配置及相关参数
    cursor.execute('DELETE FROM api_params WHERE config_id = ?', (config_id,))
    cursor.execute('DELETE FROM api_history WHERE config_id = ?', (config_id,))
    cursor.execute('DELETE FROM api_configs WHERE id = ?', (config_id,))
    
    conn.commit()
    conn.close()
    
    flash('API配置已成功删除', 'success')
    return redirect(url_for('index'))

# 获取API配置详情
@app.route('/config/<int:config_id>', methods=['GET'])
def get_config(config_id):
    conn = sqlite3.connect('instance/api_test.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取配置信息
    cursor.execute('SELECT * FROM api_configs WHERE id = ?', (config_id,))
    config = cursor.fetchone()
    
    # 获取参数信息
    cursor.execute('SELECT * FROM api_params WHERE config_id = ?', (config_id,))
    params = cursor.fetchall()
    
    conn.close()
    
    if not config:
        return jsonify({'error': '未找到API配置'}), 404
    
    config_dict = dict(config)
    params_list = [dict(param) for param in params]
    
    return jsonify({
        'config': config_dict,
        'params': params_list
    })

# 执行API调用
@app.route('/api/execute/<int:config_id>', methods=['POST'])
def execute_api(config_id):
    print(f"开始执行API调用，配置ID: {config_id}")
    
    # 检查请求内容
    if not request.is_json:
        print(f"错误: 请求内容不是JSON格式，实际内容类型: {request.content_type}")
        return jsonify({'error': '请求必须是JSON格式'}), 400
    
    try:
        request_data = request.get_json()
        print(f"请求数据: {json.dumps(request_data, ensure_ascii=False)}")
    except Exception as e:
        print(f"解析请求JSON数据失败: {str(e)}")
        return jsonify({'error': f'解析请求数据失败: {str(e)}'}), 400
    
    conn = sqlite3.connect('instance/api_test.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 获取配置信息
        cursor.execute('SELECT * FROM api_configs WHERE id = ?', (config_id,))
        config = cursor.fetchone()
        
        if not config:
            print(f"错误: 未找到ID为{config_id}的API配置")
            conn.close()
            return jsonify({'error': '未找到API配置'}), 404
        
        print(f"找到API配置: {config['name']}, URL: {config['url']}, 方法: {config['method']}")
        
        # 获取参数信息
        cursor.execute('SELECT * FROM api_params WHERE config_id = ?', (config_id,))
        params = cursor.fetchall()
        print(f"找到{len(params)}个参数")
        
        # 准备请求数据
        url = config['url']
        method = config['method']
        
        try:
            headers = json.loads(config['headers'] or '{}')
        except json.JSONDecodeError as e:
            print(f"解析请求头JSON失败: {str(e)}")
            headers = {}
        
        # 更新请求头
        custom_headers = request_data.get('headers', {})
        headers.update(custom_headers)
        print(f"最终请求头: {json.dumps(headers, ensure_ascii=False)}")
        
        # 准备请求参数
        query_params = {}
        body_params = {}
        
        # 添加默认参数
        for param in params:
            if param['param_type'] == 'query':
                query_params[param['param_name']] = param['param_value']
            elif param['param_type'] == 'body':
                body_params[param['param_name']] = param['param_value']
        
        # 添加/覆盖自定义参数
        custom_params = request_data.get('params', {})
        for key, value in custom_params.items():
            param_type = value.get('type', 'query')
            param_value = value.get('value', '')
            
            if param_type == 'query':
                query_params[key] = param_value
            elif param_type == 'body':
                body_params[key] = param_value
        
        print(f"查询参数: {json.dumps(query_params, ensure_ascii=False)}")
        print(f"请求体参数: {json.dumps(body_params, ensure_ascii=False)}")
        
        # 执行请求
        print(f"开始执行{method}请求到{url}")
        start_time = datetime.now()
        try:
            if method == 'GET':
                response = requests.get(url, params=query_params, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, params=query_params, json=body_params, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, params=query_params, json=body_params, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, params=query_params, headers=headers, timeout=30)
            else:
                print(f"错误: 不支持的HTTP方法 {method}")
                conn.close()
                return jsonify({'error': f'不支持的HTTP方法: {method}'}), 400
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            print(f"请求完成，状态码: {response.status_code}, 执行时间: {execution_time}秒")
            
            # 尝试解析JSON响应
            try:
                response_data = response.json()
                response_text = json.dumps(response_data, ensure_ascii=False, indent=2)
                print(f"成功解析JSON响应")
            except Exception as e:
                response_text = response.text
                print(f"响应不是JSON格式，使用文本格式: {str(e)}")
            
            # 保存请求历史
            request_data_to_save = {
                'url': url,
                'method': method,
                'headers': headers,
                'query_params': query_params,
                'body_params': body_params
            }
            
            try:
                cursor.execute(
                    'INSERT INTO api_history (config_id, request_data, response_data, status_code, execution_time) VALUES (?, ?, ?, ?, ?)',
                    (config_id, json.dumps(request_data_to_save), response_text, response.status_code, execution_time)
                )
                conn.commit()
                print(f"已保存请求历史记录")
            except Exception as e:
                print(f"保存历史记录失败: {str(e)}")
            
            result = {
                'status_code': response.status_code,
                'execution_time': execution_time,
                'headers': dict(response.headers),
                'response': response_text
            }
            
            conn.close()
            print(f"API调用完成，返回结果")
            return jsonify(result)
        
        except requests.exceptions.Timeout:
            print(f"错误: 请求超时")
            conn.close()
            return jsonify({'error': '请求超时，请检查API地址是否正确或稍后重试'}), 504
        except requests.exceptions.ConnectionError:
            print(f"错误: 连接错误，无法连接到{url}")
            conn.close()
            return jsonify({'error': f'连接错误，无法连接到{url}，请检查API地址是否正确'}), 502
        except requests.exceptions.RequestException as e:
            print(f"错误: 请求异常: {str(e)}")
            conn.close()
            return jsonify({'error': f'请求异常: {str(e)}'}), 500
        except Exception as e:
            print(f"错误: 执行请求时发生未知错误: {str(e)}")
            conn.close()
            return jsonify({'error': f'执行请求时发生错误: {str(e)}'}), 500
    
    except Exception as e:
        print(f"错误: API执行过程中发生未知错误: {str(e)}")
        conn.close()
        return jsonify({'error': f'API执行过程中发生错误: {str(e)}'}), 500

# 获取API调用历史
@app.route('/api/history/<int:config_id>', methods=['GET'])
def get_api_history(config_id):
    conn = sqlite3.connect('instance/api_test.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM api_history WHERE config_id = ? ORDER BY created_at DESC LIMIT 10', (config_id,))
    history = cursor.fetchall()
    
    conn.close()
    
    history_list = [dict(item) for item in history]
    return jsonify(history_list)

if __name__ == '__main__':
    app.run(debug=True)