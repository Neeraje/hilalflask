from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# متغير لحفظ آخر "مفتاح" تم استخدامه لمنع التكرار
LAST_USED_KEY = None

@app.route('/')
def hello():
    return 'Hello, world'

@app.route('/test')
def test():
    return 'Test'

@app.route('/result')
def result():
   dict = {'phy':50,'che':60,'maths':70}
   return render_template('result.html', result = dict)

# المسار الجديد لإعادة تشغيل مساحة Hugging Face
@app.route('/restart_space', methods=['GET'])
def restart_space():
    global LAST_USED_KEY
    
    # 1. استلام البيانات المشفرة والمفتاح
    hex_space_id = request.args.get('space_id')
    hex_cookie = request.args.get('cookie')
    req_key = request.args.get('key')
    
    # التحقق من وجود جميع البيانات
    if not hex_space_id or not hex_cookie or not req_key:
        return jsonify({"error": "الرجاء إرسال space_id, cookie, و key"}), 400
        
    # 2. التحقق من المفتاح لمنع التكرار
    if req_key == LAST_USED_KEY:
        return jsonify({
            "status": "ignored", 
            "message": "تم تجاهل الطلب. هذا المفتاح تم استخدامه بالفعل."
        }), 200
        
    # 3. فك تشفير البيانات من Hex إلى نصوص عادية
    try:
        space_id = bytes.fromhex(hex_space_id).decode('utf-8')
        cookie = bytes.fromhex(hex_cookie).decode('utf-8')
    except ValueError:
        return jsonify({"error": "فشل فك التشفير. تأكد من أن البيانات بصيغة Hex صحيحة."}), 400

    # 4. تكوين الرابط وإرسال الطلب إلى Hugging Face
    target_url = f'https://huggingface.co/api/spaces/{space_id}/restart'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json',
        'content-type': 'application/json',
        'origin': 'https://huggingface.co',
        'referer': f'https://huggingface.co/spaces/{space_id}',
        'Cookie': cookie  # وضع الكوكيز هنا
    }
    
    try:
        # إرسال طلب POST لـ Hugging Face
        response = requests.post(target_url, headers=headers, timeout=30)
        
        # حفظ المفتاح الجديد لأن العملية تمت
        LAST_USED_KEY = req_key
        
        # محاولة قراءة الرد كـ JSON
        try:
            hf_response = response.json()
        except:
            hf_response = response.text
            
        return jsonify({
            "status": "success",
            "message": "تم إرسال الطلب بنجاح إلى Hugging Face",
            "hf_response": hf_response,
            "http_code": response.status_code
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"cURL/Requests Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
