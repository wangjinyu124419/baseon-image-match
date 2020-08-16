import hashlib
import os
from redis import Redis
from PIL import Image
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES
from gevent.pool import Pool,joinall

es = Elasticsearch()

print(es.cluster)
ses = SignatureES(es)
redis_client = Redis()
pool = Pool(100)
print('初始化完毕')


def insert_es(img_path):
    is_valid = validate(img_path)
    if not is_valid:
        return
    try:
        ses.add_image(img_path)
    except Exception as e:
        print(e)
    else:
        print(img_path)
        img_path_hash = get_md5(img_path)
        redis_client.set(img_path_hash, 1)


def get_md5(file_path):
    md5_obj = hashlib.md5()
    md5_obj.update(file_path.encode('utf-8'))
    hash_code = md5_obj.hexdigest()
    return hash_code

def validate(image_path):
    # try:
    #     Image.open(image_path)
    # except Exception as e:
    #     print(e, image_path)
    #     return  False
    format = image_path.split('.')[-1].lower()
    if format not in ['jpg','png','gif','jpeg','bmp']:
        return False
    # file_md5 = get_md5(image_path)
    file_hash = get_md5(image_path)
    exist = redis_client.get(file_hash)
    if exist:
        print("已入库:%s" % image_path)
        return False
    return True
    # return file_md5

def handle_one(path):
    print('处理根目录:%s'%path)
    pool_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            image_path = os.path.join(root, file)
            pool_list.append(pool.spawn(insert_es, image_path))
    joinall(pool_list)


def main():
    print('启动程序')
    all_root_path_list = ['K:\新建文件夹','K:\爬虫','F:\新建文件夹','H:\新建文件夹']
    # all_root_path_list = ['K:\新建文件夹']
    for root_path in all_root_path_list:
        handle_one(root_path)
if __name__ == '__main__':
    main()
