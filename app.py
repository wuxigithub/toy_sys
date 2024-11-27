from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont


app = Flask(__name__)

DATA_PATH = 'data/toys.xlsx'
cart = {}  # 全局购物车字典 {玩具编号: {"name": 名称, "price": 价格, "quantity": 数量}}



def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_excel(DATA_PATH)
        return df.to_dict(orient='records')
    return []

@app.route('/')
def index():
    toys = load_data()
    return render_template('index.html', toys=toys, cart=cart)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    toy_id = request.json.get('toy_id')
    toys = load_data()
    toy = next((item for item in toys if item['玩具编号'] == toy_id), None)
    if toy:
        if toy_id in cart:
            cart[toy_id]['quantity'] += 1
        else:
            cart[toy_id] = {"name": toy['玩具名称'], "price": toy['价格'], "quantity": 1}
    return jsonify({"success": True, "cart": cart})

@app.route('/update_cart', methods=['POST'])
def update_cart():
    data = request.get_json()
    toy_id = data.get('toy_id')
    quantity = int(data.get('quantity'))
    
    # 删除或更新购物车项
    if toy_id in cart:
        if quantity > 0:
            cart[toy_id]['quantity'] = quantity
        else:
            del cart[toy_id]  # 如果数量为 0，删除购物车项
    
    return jsonify({"success": True, "cart": cart})

@app.route('/cart')
def cart_view():
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total_price=total_price)

@app.route('/cart_data', methods=['GET'])
def cart_data():
    return jsonify({"cart": cart})

@app.route('/generate_invoice', methods=['GET'])
def generate_invoice():
    # print("购物车内容:", cart)
    # 设置图片宽高
    img_width = 600
    img_height = 100 + len(cart) * 40 + 60  # 动态高度根据购物车内容调整
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)

    # 设置字体
    font_path = "static/fonts/仿宋_GB2312.ttf"   # 替换为适合的字体路径
    font = ImageFont.truetype(font_path, 20)

    # 标题
    y_offset = 20
    draw.text((img_width // 2 - 50, y_offset), "购物清单", font=font, fill="black")
    y_offset += 40

    # 表头
    draw.text((50, y_offset), "序号", font=font, fill="black")
    draw.text((150, y_offset), "商品名称", font=font, fill="black")
    draw.text((350, y_offset), "单价", font=font, fill="black")
    draw.text((450, y_offset), "数量", font=font, fill="black")
    draw.text((500, y_offset), "总价", font=font, fill="black")
    y_offset += 30

    # 遍历购物车内容
    total_price = 0
    for idx, (toy_id, item) in enumerate(cart.items()):
        draw.text((50, y_offset), str(idx + 1), font=font, fill="black")
        draw.text((150, y_offset), item['name'], font=font, fill="black")
        draw.text((350, y_offset), f"{item['price']} 元", font=font, fill="black")
        draw.text((450, y_offset), str(item['quantity']), font=font, fill="black")
        item_total = item['price'] * item['quantity']
        draw.text((500, y_offset), f"{item_total} 元", font=font, fill="black")
        total_price += item_total
        y_offset += 30

    # 总价
    draw.text((350, y_offset + 20), f"总价: {total_price} 元", font=font, fill="black")

    # 保存图片
    img_path = "static/invoice.png"
    img.save(img_path)

    # 返回图片
    return send_file(img_path, mimetype='image/png')


    
if __name__ == '__main__':
    app.run(debug=True,port=5001)