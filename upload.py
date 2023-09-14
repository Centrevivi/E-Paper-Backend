from flask import Flask, request, render_template, jsonify
from flask_restful import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage
from PIL import Image
from converter import image_driver
import os

from unit import Unit



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # 允许的图片文件扩展名

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def configure_upload(app):
    # 添加一个路由来处理文件上传
    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # 检查是否有文件被上传
            if 'file' not in request.files:
                return 'No file part'
            
            file = request.files['file']

            # 如果用户未选择文件，浏览器会发送一个空文件
            if file.filename == '':
                return 'No selected file'
            
            if allowed_file(file.filename) == False:
                return '请上传图片文件'
            
            # 如果文件存在，保存它
            if file:
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                return 'File uploaded successfully'

        return render_template('upload.html')

class FileUpload(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=FileStorage, location='files')
        args = parser.parse_args()
        uploaded_file = args['file']

        if uploaded_file:
            filename = os.path.join(Unit.app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            image = Image.open(uploaded_file)
            image = image.convert('RGB')
            jpeg_filename = os.path.splitext(filename)[0] + '.jpg'
            image.save(jpeg_filename, format='JPEG', quality=100)
            with Image.open(jpeg_filename) as img:
                # 设置图片质量为85，以控制压缩程度
                quality = 85
                # 检查文件大小，如果大于2MB，则继续压缩
                while os.path.getsize(jpeg_filename) > (2 * 1024 * 1024):  # 2MB
                    quality = quality - 5
                    img.save(jpeg_filename, format='JPEG', quality=quality) 
                    print(os.path.getsize(jpeg_filename))
            
            send_img = Image.open(jpeg_filename)
            Unit.data = image_driver(send_img)
            
            return {'message': 'File uploaded successfully', 'filename': jpeg_filename}
        else:
            return {'message': 'No file uploaded'}, 400