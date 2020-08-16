import hashlib
import os

import numpy as np
from PIL import Image
# from feature_extractor import FeatureExtractor
from datetime import datetime
from flask import Flask, request, render_template
from pathlib import Path

app = Flask(__name__)
import time
from elasticsearch import Elasticsearch

from image_match.elasticsearch_driver import SignatureES
from pathlib import Path

# es = Elasticsearch(hosts='192.168.3.8',port=9400)
es = Elasticsearch()
ses = SignatureES(es, distance_cutoff=0.55)


def get_md5(file_obj):
    md5_obj = hashlib.md5()
    md5_obj.update(file_obj.read())
    hash_code = md5_obj.hexdigest()
    file_md5 = str(hash_code).lower()
    return file_md5


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['query_img']
        if not file:
            return '请添加文件'

        # Save query image
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = "static\\uploaded\\" + get_md5(file.stream) + '.jpg'
        img.save(uploaded_img_path)

        # Run search
        res = ses.search_image(uploaded_img_path, all_orientations=True)
        if not res:
            return '未找到匹配项'
        scores = [(r['path'], r['id']) for r in res]

        return render_template('index.html',
                               query_path=uploaded_img_path,
                               scores=scores)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    # app.run("0.0.0.0")
    app.run()
