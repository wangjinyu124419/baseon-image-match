import hashlib
import os

from PIL import Image
from elasticsearch import Elasticsearch
# from feature_extractor import FeatureExtractor
from flask import Flask, request, render_template

from image_match.elasticsearch_driver import SignatureES
from local_config import ES_HOST, ES_PORT, UPLOAD_PATH, STATIC_FOLDER, STATIC_URL_PATH

# app = Flask(__name__,static_folder=r'E:\爬虫',static_url_path='/test')
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path=STATIC_URL_PATH)
print(app.static_url_path)
# app.static_folder = 'D:\PycharmProjects\sis\static2'
# app.static_url_path = 'static2'


es = Elasticsearch(hosts=ES_HOST, port=ES_PORT)
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
        file_format = file.filename.split('.')[-1]
        file_name = get_md5(file.stream) + '.' + file_format

        # uploaded_img_path =STATIC_FOLDER + UPLOAD_PATH + get_md5(file.stream) + '.jpg'
        uploaded_img_path = os.path.join(STATIC_FOLDER, UPLOAD_PATH, file_name)

        # Save query image
        img = Image.open(file.stream)  # PIL image
        if not os.path.exists(uploaded_img_path):
            img.save(uploaded_img_path)

        # Run search
        res = ses.search_image(uploaded_img_path, all_orientations=True)
        if not res:
            return '未找到匹配项'
        # scores = [('static/'+r['path'].split('\\',maxsplit=1)[1], r['id']) for r in res]
        scores = [(os.path.join(STATIC_URL_PATH, r['path'].split('\\', maxsplit=1)[1]), r['path'], r['id']) for r in
                  res]
        # scores = [(r['path'], r['id']) for r in res]

        return render_template('index.html',
                               # query_path='static/'+uploaded_img_path,
                               query_path=os.path.join(STATIC_URL_PATH, UPLOAD_PATH, file_name),
                               scores=scores)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    # app.run("0.0.0.0")
    app.run()
