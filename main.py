import json
import time
import hashlib

import tornado.ioloop
import tornado.web
import os
from cert_imgs_db import CertImagesDB
from doc_util import cert_img_to_doc, save_doc


# 主入口
class MainHandler(tornado.web.RequestHandler):

    def get(self):
        db = CertImagesDB()
        succ, msg, data = db.query(None);
        # print(data)
        self.render("index.html", succ=succ, msg=msg, data=data, len=len)


# 查询
class QueryHandler(tornado.web.RequestHandler):
    def get(self):
        db = CertImagesDB()
        succ, msg, data = db.query(None);
        # print(data)
        self.write(json.dumps({
            'success': succ,
            'msg': msg,
            'data': data
        }))
        # self.render("500.html", msg="后台有错")  # 模板参数传递


# 新增
class AddHandler(tornado.web.RequestHandler):
    def post(self):
        param = tornado.escape.json_decode(self.request.body)

        if not 'name' in param or param['name'] is None:
            self.write(json.dumps({
                'success': False,
                'msg': '名称不可为空'
            }))
            return

        if not 'images' in param or param['images'] is None:
            self.write(json.dumps({
                'success': False,
                'msg': '图片不可为空'
            }))
            return

        record = {
            'name': param['name'],
            'category': '' if 'category' not in param else param['category'],
            'images': [f['url'] for f in param['images']]
        }
        db = CertImagesDB()
        succ, msg, data = db.add(record)
        self.write(json.dumps({
            'success': succ,
            'msg': msg,
            'data': data
        }))
        # self.render("500.html", msg="后台有错")  # 模板参数传递


class DeleteHandler(tornado.web.RequestHandler):
    def post(self):
        param = tornado.escape.json_decode(self.request.body)
        if not 'uk' in param or param['uk'] is None:
            self.write(json.dumps({
                'success': False,
                'msg': '删除对象不明确'
            }))
        db = CertImagesDB()
        succ, msg = db.delete(param['uk']);
        self.write(json.dumps({
            'success': succ,
            'msg': msg,
        }))


class GenDocHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        param = tornado.escape.json_decode(self.request.body)
        if 'records' in param:
            records = param['records']
        elif 'uks' in param:
            uks = param['uks']
            db = CertImagesDB()
            succ, msg, records = db.query_by_uks(uks);
            if not succ:
                self.write({
                    'success': succ,
                    'msg': msg,
                })
                return

        # print(records)
        watermark_text = param['watermarkText'] if 'watermarkText' in param else None
        need_title = bool(param['needTitle']) if 'needTitle' in param else True
        now = time.strftime("%Y-%m-%d %H-%M-%S")
        out_dir = os.path.join('web', 'docs', now)
        succ, msg = False, ''
        try:
            doc = cert_img_to_doc(records=records, out_dir=out_dir,
                                  watermark_text=watermark_text, need_title=need_title)
            path = save_doc(doc, os.path.join(out_dir, 'export.docx'))
            succ, msg = True, '导出成功'
        except Exception as e:
            succ, msg = False, '导出失败'
        finally:
            self.write(json.dumps({
                'success': succ,
                'msg': msg,
                'path': path,
                'data': None if path is None else ('/cert-docs' + path.split(os.path.join('web', 'docs'))[1])
            }))
        # self.render("500.html", msg="后台有错")  # 模板参数传递


# 上传
class UploadHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        file_metas = self.request.files["file"]
        for meta in file_metas:  # 循环文件信息
            file_name = meta['filename']  # 获取文件的名称
            md5hash = hashlib.md5(meta['filename'].encode("utf-8"))
            md5 = md5hash.hexdigest()
            save_name = md5 + os.path.splitext(file_name)[-1]
            with open(os.path.join('web/static/upload', save_name), 'wb') as up:  # os拼接文件保存路径，以字节码模式打开
                up.write(meta['body'])
                self.write({
                    'name': file_name,
                    'save_name': save_name,
                    'path': 'upload/' + save_name,
                    'url': '/upload/' + save_name
                })


class UploadCertImgHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        file_metas = self.request.files["file"]
        for meta in file_metas:  # 循环文件信息
            file_name = meta['filename']  # 获取文件的名称
            md5hash = hashlib.md5(meta['filename'].encode("utf-8"))
            md5 = md5hash.hexdigest()
            save_name = md5 + os.path.splitext(file_name)[-1]
            with open(os.path.join('data', 'cert-image', save_name), 'wb') as up:  # os拼接文件保存路径，以字节码模式打开
                up.write(meta['body'])
                self.write({
                    'name': file_name,
                    'save_name': save_name,
                    'path': 'cert-image/' + save_name,
                    'url': '/cert-imgs/' + save_name
                })


class APIHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("500.html", msg="后台有错")  # 模板参数传递


class ErrorHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("500.html", msg="后台有错")  # 模板参数传递


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),

            ("/cert-imgs/(.*)", tornado.web.StaticFileHandler, {'path': 'data/cert-image'}),
            ("/cert-docs/(.*)", tornado.web.StaticFileHandler, {'path': 'web/docs'}),
            ("/upload/(.*)", tornado.web.StaticFileHandler, {'path': 'web/static/upload'}),
            (r"/api/query", QueryHandler),
            (r"/api/add", AddHandler),
            (r"/api/delete", DeleteHandler),
            (r"/api/gen_doc", GenDocHandler),
            (r"/api/upload-cert-img", UploadCertImgHandler),
            (r"/api/upload", UploadHandler),

            # ("/(.*)", tornado.web.StaticFileHandler, {'path': 'web/templates', 'default_filename': 'index.html'}),
        ],
        template_path=os.path.join(
            os.path.dirname(__file__), "web/templates"  # 索引到templates文件夹中的html
        ),
        static_path=os.path.join(os.path.dirname(__file__), "web/static"),

        debug=True
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
