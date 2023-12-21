# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: api_file_upload.py
# @time: 2023/7/22 16:41
import os
import traceback

from flask import request, jsonify, Blueprint

from data_process.data_processor import DataProcessor


api_file_upload = Blueprint('api_file_upload', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
UPLOAD_FILE_PATH = './files'

html = '''
    <!DOCTYPE html>
    <title>Upload File</title>
    <h1>File Sumbit</h1>
    <form method=post enctype=multipart/form-data>
         <p>FILE: <input type=file name=file><br></p>
         <p>URL PARSE: <input name="url" type="url" class="form-control" id="url"><br></p>
         <p>INPUT SOURCE: <input name="source" type="input_source" class="form-control" id="source"><br></p>
         <p>INPUT CONTEXT: <textarea name="context" rows="10" cols="40" type="context" class="form-control" id="context"></textarea><br></p>
         <input type=submit value=Sumbit>
    </form>
    '''


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@api_file_upload.route('/api/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        url = request.form['url']
        input_source = request.form['source']
        input_context = request.form['context']
        if input_source and input_context:
            while '\n\n' in input_context:
                input_context = input_context.replace('\n\n', '\n')
            while '\r\n' in input_context:
                input_context = input_context.replace('\r\n', '\n')
            return_data = {"source": input_source, "context": input_context, "parse": "ok!", "error": ""}
            try:
                DataProcessor(input_source, input_context).data_insert()
            except Exception:
                return_data["parse"] = "fail!"
                return_data["error"] = traceback.format_exc()
            return jsonify(return_data)

        elif url:
            return_data = {"url": url, "parse": "ok!", "error": ""}
            try:
                DataProcessor(url).data_insert()
            except Exception:
                return_data["parse"] = "fail!"
                return_data["error"] = traceback.format_exc()
            return jsonify(return_data)
        else:
            file = request.files['file']
            file_name = file.filename
            if file and allowed_file(file_name):
                file_path = os.path.join(UPLOAD_FILE_PATH, file_name)
                if os.path.exists(file_path):
                    return f"The file <mark>{file_name}</mark> already existed!"
                file.save(file_path)
                # 解析文本
                DataProcessor(file_path).data_insert()
                return jsonify({"upload file": file_name,
                                "ES": "ok!",
                                "Milvus": "ok!"})
    return html
