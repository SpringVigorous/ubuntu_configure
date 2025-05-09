from flask import Flask, request, jsonify,render_template
from flask_cors import CORS 
from tea_manager import TeaInventorySystem
import os
import json
def get_json_data():
    if request.is_json:
        return request.get_json()
    else:
        try:
            return json.loads(request.data)
        except:
            return None
    
    
    
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化库存系统
inventory = TeaInventorySystem(
    host='localhost',
    database='medical_product',
    user='SpringFlourish',
    password='137098',
    port=3306,
    pool_size=3
)
@app.route('/')
def index():

    try:
        herbs = inventory.get_all_herbs()  # 获取药材列表
        return render_template('index.html', 
                             herbs=herbs,
                             page_title="药材库存")
    except Exception as e:
        return render_template('error.html', error=str(e))
    
@app.route('/api/herbs', methods=['GET'])
def get_all_herbs():
    """获取所有药材"""
    herbs = inventory.get_all_herbs()
    return jsonify({'success': True, 'data': herbs})



@app.route('/api/herbs', methods=['POST'])
def add_herb():
    """添加新药材"""
    data = get_json_data()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    herb_id = inventory.add_herb(
        name=data['name'],
        scientific_name=data.get('scientific_name', ''),
        specification=data.get('specification', ''),
        unit=data.get('unit', '克')
    )
    if herb_id:
        return jsonify({'success': True, 'herb_id': herb_id})
    return jsonify({'success': False, 'message': '添加失败'}), 400

@app.route('/api/inventory/herbs', methods=['POST'])
def stock_in_herb():
    """药材入库"""
    data = get_json_data()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    success = inventory.stock_in_herb(
        herb_id=data['herb_id'],
        quantity=data['quantity'],
        batch_number=data['batch_number'],
        operator=data['operator'],
        production_date=data['production_date'],
        expiry_date=data['expiry_date']
    )
    return jsonify({'success': success})

@app.route('/api/undo', methods=['POST'])
def undo_last_operation():
    """撤销操作"""
    success = inventory.undo_last_operation()
    return jsonify({'success': success})

if __name__ == '__main__':
    
    host='localhost',
    database='tea_inventory',
    user='root',
    password='password'
    
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    
    """
    运行：1 直接运行tea_app.py
    2.  在cmd中运行，进入当前文件目录，执行以下命令
    set FLASK_APP=tea_app.py
    set FLASK_ENV=development
    flask run
    """