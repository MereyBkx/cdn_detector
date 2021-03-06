"""
Author: Sun Peishuai
Date: 2020-12-08
"""
# from  CDN.models import CDN_urls
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotFound
# 增加对分页的支持
import sys
sys.path.append("../..")
import json
from database.database_sql import operation
from database.database_sql import mysql_neo4j
from database.database import session
#from sqlalchemy.ext.declarative import declarative_base
sys.path.append("../../back-end")
from back_end.Server_communication import multi_request_domain
from utils.utils import logger_django as logger
import ipdb




def listorders(request):
    try:
        # 将请求参数统一放入request 的 params 属性中，方便后续处理
        # GET请求 参数在url中，同过request 对象的 GET属性获取
        if request.method == 'GET':
            request = request.GET
        # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
        elif request.method in ['POST', 'PUT', 'DELETE']:
            # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
            request = json.loads(request.body)

        # 根据不同的action分派给不同的函数进行处理
        action = request.get("domain",None)
        if action:
            return mysql(request,action)
        else:
            return HttpResponseNotFound("Not Found!")
    except Exception as e:
        logger.error(" error, HTTP {}".format(e))
        return HttpResponseServerError("内部错误!")
    finally:
        if action:
            logger.info(" info, 成功请求domain:{}".format(action))

def mysql(request,domain):
    # 数据库连接初始化
    try:
        #ipdb.set_trace()
        op = operation(session)
        if op.is_exist(domain):
            pass
        else:
            result = multi_request_domain(domain)
            op.op_add(result)
        #查找该域名以及底下的CDN
        cname_all_list,a_all_list,cdn_list=op.op_select(domain)
        nodes,edges=mysql_neo4j(cname_all_list,a_all_list,cdn_list)
        neo4j_=(nodes,edges)
        #ipdb.set_trace()
        if nodes == [] and edges == []:
            return HttpResponseBadRequest("{} 无结果".format(domain))
        else:
            return JsonResponse({'ret': 0, 'mysql_lists':a_all_list,"cdn_list":cdn_list,"neo4j_":neo4j_})
    except Exception as e:
        logger.error("func mysql error: {}".format())
        return HttpResponseServerError("内部错误!")



