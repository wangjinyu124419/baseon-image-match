import hashlib
import os
from base64 import b64encode

from elasticsearch import Elasticsearch
from flask import Flask, request, render_template

from image_match.elasticsearch_driver import SignatureES
from local_config import ES_HOST, ES_PORT, STATIC_FOLDER, STATIC_URL_PATH

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path=STATIC_URL_PATH)
print(app.static_url_path)

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
        raw_file = file.read()
        res = ses.search_image(raw_file, all_orientations=True, bytestream=True)
        if not res:
            return '未找到匹配项'
        scores = [(os.path.join(STATIC_URL_PATH, r['path'].split('\\', maxsplit=1)[1]), r['path'], r['id']) for r in
                  res]
        b64_data = str(b64encode(raw_file), 'utf-8')
        query_path = "data:image/jpeg;base64,{}".format(b64_data)
        return render_template('index.html',
                               query_path=query_path,
                               scores=scores)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    # app.run("0.0.0.0")
    app.run()
