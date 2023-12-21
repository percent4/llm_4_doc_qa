# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: server.py
# @time: 2023/6/5 17:05
from flask import Flask

from views.api_doc_qa import api_doc_qa
from views.api_file_upload import api_file_upload

from config.config_parser import SERVER_HOST, SERVER_PORT

app = Flask('doc_qa')
app.register_blueprint(api_doc_qa)
app.register_blueprint(api_file_upload)


@app.route("/api/health", methods=["GET"])
def health_check() -> str:
    return '200'


if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)
