#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/30 15:46
# @Author  : ma.fei
# @File    : t_user.py
# @Software: PyCharm

import os
import requests
import traceback
from   web.model.t_db_inst import query_inst_by_id,get_ds_by_instid
from   web.model.t_sql_release import  format_sql
from   web.utils.mysql_async import async_processer

def check_slow(p_slow):
    result = {}
    if p_slow["slow_time"]=="":
        result['code']='-1'
        result['message']='慢查询时长不能为空！'
        return result

    if p_slow["python3_home"]=="":
        result['code']='-1'
        result['message']='python3目录不能为空！'
        return result

    if p_slow["script_path"]=="":
        result['code']='-1'
        result['message']='脚本路径不能为空！'
        return result

    if p_slow["api_server"]=="":
        result['code']='-1'
        result['message']='API服务器不能为空！'
        return result


    if if_exists_slow(p_slow["inst_id"]):
        result['code'] = '-1'
        result['message'] = '慢日志已存在！'
        return result

    result['code'] = '0'
    result['message'] = '验证通过'
    return result

def push_slow(p_api,p_slowid):
    url = 'http://{}/push_slow_remote'.format(p_api)
    res = requests.post(url, data={'slow_id': p_slowid})
    jres = res.json()
    v = ''
    for c in jres['msg']['crontab'].split('\n'):
        if c.count(p_slowid) > 0:
            v = v + "<span class='warning'>" + c + "</span>"
        else:
            v = v + c
        v = v + '<br>'
    jres['msg']['crontab'] = v
    return jres

async def query_slow(p_inst_id,p_inst_env):
    vv  = ''
    if p_inst_id != '':
        vv = "  where a.inst_id ='{0}' ".format(p_inst_id)
    if p_inst_env != '':
        vv = vv +"  and b.inst_env ='{0}' ".format(p_inst_env)
    sql = """select a.id, b.inst_name,
                   (SELECT dmmc FROM t_dmmx X WHERE x.dm='03' AND x.dmm=b.inst_env) AS env_name,
                    a.log_file,
                    a.query_time,
                    a.script_file,
                    a.api_server,
                    case a.status when '1' then '是'  when '0' then '否'  end  status,
                    date_format(create_date,'%Y-%m-%d')    create_date
             from t_slow_log a,t_db_inst b where a.inst_id=b.id {} order by a.id""".format(vv)
    return await async_processer.query_list(sql)

async def query_slow_log(p_inst_id,p_db_name,p_db_user,p_db_host,p_begin_date,p_end_date):
    vv  = ''
    if p_inst_id != '':
        vv = "  where a.inst_id ='{0}' ".format(p_inst_id)
    if p_begin_date != '':
        vv = vv + " and a.finish_time>='{0}'\n".format(p_begin_date)
    if p_end_date != '':
        vv = vv + " and a.finish_time<='{0}'\n".format(p_end_date)
    if p_db_name != '':
        vv = vv + "  and a.db ='{0}' ".format(p_db_name)
    if p_db_user != '':
        vv = vv + "  and a.user ='{0}' ".format(p_db_user)
    if p_db_host != '':
        vv = vv + "  and instr(a.host,'{0}')>0".format(p_db_host)

    sql = """SELECT 
                  a.sql_id,a.user,a.db,a.host,cast(ROUND(a.query_time+0,2) as char) AS exec_time,
                  a.bytes,DATE_FORMAT(a.finish_time,'%Y-%m-%d %H:%i:%s') AS create_date
                FROM t_slow_detail a {} order by a.finish_time desc """.format(vv)
    return await async_processer.query_list(sql)

async def get_slowid():
    rs = await  async_processer.query_one("select ifnull(max(id),0)+1 from t_role")
    return rs[0]

async def get_slow_by_slowid(p_slowid):
    sql="select * from t_slow_log where id={0}".format(p_slowid)
    return await  async_processer.query_dict_one(sql)

async def get_slows():
    sql="select cast(id as char) as id,name from t_role where status='1'"
    return await async_processer.query_list(sql)

async def if_exists_slow(p_inst_id):
    sql="select count(0) from t_slow_log where inst_id='{0}'".format(p_inst_id)
    rs =await  async_processer.query_one(sql)
    if rs[0]==0:
        return False
    else:
        return True

async def save_slow(p_slow):
    val = check_slow(p_slow)
    if val['code'] == '-1':
        return val
    try:
        inst_id       = p_slow['inst_id']
        server_id     = p_slow['server_id']
        slow_time     = p_slow['slow_time']
        slow_log_name = p_slow['slow_log_name']
        python3_home  = p_slow['python3_home']
        run_time      = p_slow['run_time']
        exec_time     = p_slow['exec_time']
        script_path   = p_slow['script_path']
        script_file   = p_slow['script_file']
        slow_status   = p_slow['slow_status']
        api_server    = p_slow['api_server']
        sql="""insert into t_slow_log(inst_id,server_id,log_file,query_time,python3_home,run_time,exec_time,script_path,script_file,status,api_server,create_date) 
                 values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}',now())
            """.format(inst_id,server_id,slow_log_name,slow_time,python3_home,run_time,exec_time,script_path,script_file,slow_status,api_server)
        await async_processer.exec_sql(sql)

        sql = """INSERT INTO t_db_inst_parameter(inst_id,NAME,VALUE,TYPE,STATUS,create_date) 
                             VALUES({},'慢日志开关'  ,'{}','mysqld','1',NOW()),
                                   ({},'慢日志文件名','{}','mysqld','1',NOW()),
                                   ({},'慢日志时长'  ,'{}','mysqld','1',NOW()) 
            """.format(inst_id, 'slow_query_log={}'.format('ON' if slow_status == '1' else 'OFF'),
                       inst_id, 'slow_query_log_file=''{{}}/{}'''.format(slow_log_name),
                       inst_id,'long_query_time={}'.format(slow_time))
        await async_processer.exec_sql(sql)
        return {'code': '0', 'message': '保存成功!'}
    except:
        traceback.print_exc()
        return {'code': '-1', 'message': '保存失败!'}

async def upd_slow(p_slow):
    try:
        slow_id        = p_slow['slow_id']
        inst_id        = p_slow['inst_id']
        server_id      = p_slow['server_id']
        slow_time      = p_slow['slow_time']
        slow_log_name  = p_slow['slow_log_name']
        python3_home   = p_slow['python3_home']
        run_time       = p_slow['run_time']
        exec_time      = p_slow['exec_time']
        script_path    = p_slow['script_path']
        script_file    = p_slow['script_file']
        slow_status    = p_slow['slow_status']
        api_server     = p_slow['api_server']
        sql="""update t_slow_log
                  set  inst_id        ='{}' ,
                       server_id      ='{}' ,
                       query_time     ='{}' ,
                       log_file       ='{}' ,
                       python3_home   ='{}' ,
                       run_time       ='{}' ,
                       exec_time      ='{}' ,
                       script_path    ='{}' ,
                       script_file    ='{}' ,
                       api_server     ='{}' ,
                       status         ='{}' ,
                       last_update_date =now() 
                where id='{}'
            """.format(inst_id,server_id,slow_time,slow_log_name,python3_home,run_time,exec_time,script_path,script_file,api_server,slow_status,slow_id)
        await async_processer.exec_sql(sql)

        sql = """delete from  t_db_inst_parameter 
                  where inst_id={} 
                   and (value like 'slow_query_log%' or value like 'long_query_time%')""".format(inst_id)
        await async_processer.exec_sql(sql)

        sql = """INSERT INTO t_db_inst_parameter(inst_id,NAME,VALUE,TYPE,STATUS,create_date) 
                     VALUES({},'慢日志开关'  ,'{}','mysqld','1',NOW()),
                           ({},'慢日志文件名','{}','mysqld','1',NOW()),
                           ({},'慢日志时长'  ,'{}','mysqld','1',NOW()) 
              """.format(inst_id, 'slow_query_log={}'.format('ON' if slow_status == '1' else 'OFF'),
                         inst_id, 'slow_query_log_file=''{{}}/{}'''.format(slow_log_name),
                         inst_id, 'long_query_time={}'.format(slow_time))
        await async_processer.exec_sql(sql)
        return {'code': '0', 'message': '更新成功!'}
    except :
        traceback.print_exc()
        return {'code': '-1', 'message': '更新失败!'}

async def del_slow(p_slowid):
    try:
        slow = await get_slow_by_slowid(p_slowid)
        await async_processer.exec_sql("delete from t_slow_log  where id='{0}'".format(p_slowid))
        sql = """delete from  t_db_inst_parameter 
                    where inst_id={}  and (value like 'slow_query_log%' or value like 'long_query_time%')""".format(slow['inst_id'])
        await async_processer.exec_sql(sql)
        return {'code': '0', 'message':'删除成功!'}
    except :
        traceback.print_exc()
        return {'code': '-1', 'message':'删除失败!'}

async def query_slow_by_id(p_slow_id):
    sql = """SELECT a.id,
                    a.inst_id,
                    a.server_id,
                    a.query_time,
                    a.log_file,
                    a.python3_home,
                    a.run_time,
                    a.exec_time,
                    a.script_path,
                    a.script_file,
                    a.api_server,
                    a.status,
                    date_format(a.create_date,'%Y-%m-%d %H:%i:%s')  as create_date,
                    date_format(a.last_update_date,'%Y-%m-%d %H:%i:%s')  as last_update_date 
             FROM t_slow_log a  WHERE  a.id='{0}'""".format(p_slow_id)
    return await async_processer.query_dict_one(sql)

async def query_slow_log_by_id(p_sqlid):
    sql = """SELECT a.inst_id,a.db,a.sql_text FROM t_slow_detail a  WHERE  a.sql_id='{0}' limit 1""".format(p_sqlid)
    rs  = await async_processer.query_dict_one(sql)
    rs['sql_text'] = format_sql(rs['sql_text'])['message']
    return rs

async def query_slow_log_detail(p_sqlid):
    sql = """SELECT 
                    GROUP_CONCAT(DISTINCT x.user) AS "user",
                    GROUP_CONCAT(DISTINCT x.host) AS "host",
                    GROUP_CONCAT(DISTINCT x.db)   AS "db",
                    CONCAT(GROUP_CONCAT(x.min_query_time SEPARATOR "~"),'s') AS min_query_time,
                    CONCAT(GROUP_CONCAT(x.max_query_time SEPARATOR "~"),'s') AS max_query_time,
                    GROUP_CONCAT(x.min_finish_time SEPARATOR "~") AS min_finish_time,
                    GROUP_CONCAT(x.max_finish_time SEPARATOR "~") AS max_finish_time,
                    GROUP_CONCAT(x.exec_time) AS exec_time
                FROM (SELECT a.sql_id,a.user,a.host,a.db,
                           ROUND(MIN(query_time),0)  AS min_query_time,
                           ROUND(MAX(query_time),0)  AS max_query_time,
                           MIN(finish_time) AS min_finish_time,
                           MAX(finish_time) AS max_finish_time,
                           COUNT(0)         AS exec_time     
                     FROM t_slow_detail a  WHERE  a.sql_id='{}'  GROUP BY  a.user,a.host,a.db ) X GROUP BY x.sql_id""".format(p_sqlid)
    return await async_processer.query_dict_one(sql)

async def query_slow_log_plan(p_sqlid):
    log  = await query_slow_log_by_id(p_sqlid)
    inst = await query_inst_by_id(log['inst_id'])
    with open('/tmp/{}.sql'.format(p_sqlid), 'w') as f:
        f.write(log['sql_text'])

    cmd = """pt-visual-explain -u{} -p'{}' -h{} --database={} --charset=utf8 --connect /tmp/{}.sql>/tmp/{}.sql.o
          """.format(inst['mgr_user'],inst['mgr_pass'],inst['inst_ip'],log['db'],p_sqlid,p_sqlid)
    os.system(cmd)
    with open('/tmp/{}.sql.o'.format(p_sqlid), 'r') as f:
        plan=f.readlines()
    return ''.join(plan)

async def get_db_by_inst_id(p_inst_id):
    pds = await get_ds_by_instid(p_inst_id)
    sql = """SELECT schema_name FROM information_schema.schemata 
                 WHERE schema_name NOT IN('information_schema','performance_schema','test','sys','mysql')"""
    return await async_processer.query_list_by_ds(pds,sql)

async def get_user_by_inst_id(p_inst_id):
    pds  = await get_ds_by_instid(p_inst_id)
    sql  = """SELECT distinct USER FROM mysql.user ORDER BY 1 """
    return await async_processer.query_list_by_ds(pds,sql)


async def analyze_slow_log(p_inst_id,p_db_name,p_db_user,p_db_host,p_begin_date,p_end_date):
    vv  = ''
    v_total = {}
    if p_inst_id != '':
        vv = " and a.inst_id ='{0}' ".format(p_inst_id)
    if p_db_name != '':
        vv = vv + "  and a.db ='{0}' ".format(p_db_name)
    if p_db_user != '':
        vv = vv + "  and a.user ='{0}' ".format(p_db_user)
    if p_db_host != '':
        vv = vv + "  and instr(a.host,'{0}')>0".format(p_db_host)
    if p_begin_date != '':
        vv = vv + " and a.finish_time>='{0}'\n".format(p_begin_date)
    if p_end_date != '':
        vv = vv + " and a.finish_time<='{0}'\n".format(p_end_date)

    sql_host  = """SELECT HOST as name,COUNT(0) AS value FROM t_slow_detail a where 1 =1 {} GROUP BY HOST""".format(vv)

    sql_db    = """SELECT db as name ,COUNT(0) AS value  FROM t_slow_detail a where 1 =1 {} GROUP BY db""".format(vv)

    sql_user  = """SELECT user as name ,COUNT(0) AS value FROM t_slow_detail a where 1 =1 {} GROUP BY user""".format(vv)

    sql_top10 = """SELECT CONCAT((@rowNum:=@rowNum+1),'') AS xh,sql_id,query_time,exec_time
                   FROM (SELECT sql_id,cast(ROUND(AVG(query_time),0) as char) AS query_time, count(0) as exec_time
                          FROM t_slow_detail a ,(SELECT (@rowNum:=0)) b
                           WHERE 1 =1  {} GROUP BY inst_id,sql_id  ORDER BY AVG(query_time) DESC LIMIT 10) X""".format(vv)

    v_total['host']  = await async_processer.query_dict_list(sql_host)
    v_total['db']    = await async_processer.query_dict_list(sql_db)
    v_total['user']  = await async_processer.query_dict_list(sql_user)
    v_total['top10'] = await async_processer.query_list(sql_top10)
    return v_total