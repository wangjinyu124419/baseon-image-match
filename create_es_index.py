import hashlib
import os

from PIL import ImageFile
from elasticsearch import Elasticsearch
from gevent.pool import Pool, joinall
from redis import Redis

from image_match.elasticsearch_driver import SignatureES
from local_config import IMAGE_PATHS

ImageFile.LOAD_TRUNCATED_IMAGES = True
es = Elasticsearch()

print(es.cluster)
ses = SignatureES(es)
redis_client = Redis()
pool = Pool(100)
print('初始化完毕')


def insert_es(img_path):
    if not validate_format(img_path):
        return

    file_hash = get_md5(img_path)
    if redis_client.get(file_hash):
        # print("已入库:%s" % img_path)
        return
    try:
        ses.add_image(img_path)
    except Exception as e:
        '图片入库异常,路径:{},异常:{}'.format(img_path,str(e))
        # print(traceback.format_exc())
    else:
        print('入库完成:%s' % img_path)
        redis_client.set(file_hash, 1)


def get_md5(file_path):
    md5_obj = hashlib.md5()
    md5_obj.update(file_path.encode('utf-8'))
    hash_code = md5_obj.hexdigest()
    return hash_code


def validate_format(image_path):
    # try:
    #     Image.open(image_path)
    # except Exception as e:
    #     print(e, image_path)
    #     return  False
    format = image_path.split('.')[-1].lower()
    if format not in ['jpg', 'png', 'gif', 'jpeg', 'bmp']:
        return False
    return True
    # return file_md5


def handle_one(path):
    print('处理根目录:%s' % path)
    pool_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            image_path = os.path.join(root, file)
            pool_list.append(pool.spawn(insert_es, image_path))
    joinall(pool_list)


def main():
    print('启动程序')
    all_root_path_list = IMAGE_PATHS
    # all_root_path_list = ['K:\新建文件夹']
    for root_path in all_root_path_list:
        handle_one(root_path)


if __name__ == '__main__':
    # redis_client.flushall()
    main()
