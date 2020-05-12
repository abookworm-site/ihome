# coding:utf-8
import redis
from flask import Flask
from config import config_map  # 导入启动配置映射
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect

from ihome.utils.commons import ReConverter

# 导入日志功能
import logging
from logging.handlers import RotatingFileHandler


# 创建数据库
db = SQLAlchemy()

# 创建redis 连接对象
redis_store = None

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)
# 创建日志记录器，定义日志保存的路径，每个日志文件的最大大小，保存的日志文件个数上限
file_log_handle = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日常日志记录格式
file_log_handle.setFormatter(formatter)
# 为全局的日常工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handle)


# 工厂模式
def create_app(config_name):
    """
    创建flask的应用对象
    :param config_name: str 配置模式的名字 ("develop", "product:)
    :return:
    """
    app = Flask(__name__)

    # 根据配置模式的名字获取配置参数的类
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 使用app初始化数据库db
    db.init_app(app)

    # 初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 利用flask-session, 将session数据保存到redis中
    Session(app)

    # 为flask补充csrf防护
    CSRFProtect(app)

    # 为flask添加自定义的转换器
    app.url_map.converters["re"] = ReConverter

    # 注册蓝图
    from ihome import api_1_0  # 此时导入蓝图，防止循环导包问题
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

    # 注册提供静态文件的蓝图
    from ihome import web_html
    app.register_blueprint(web_html.html)

    return app