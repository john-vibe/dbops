#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/12/14 14:02
# @Author : ma.fei
# @File : t_db_tools.py.py
# @Software: PyCharm

from web.model.t_ds import get_ds_by_dsid_by_cdb
from web.utils.common import format_sql
from web.utils.mysql_async import async_processer


async def save_db(dsid,dres):
    desc = 'insert into t_db_compare(`dsid`,'
    for r in dres[0:1]:
          for key, value in r.items():
                desc = desc + '`{}`,'.format(key)
    desc = desc[0:-1]+') values '

    vals = ''
    for r in dres:
          val = '{},'.format(dsid)
          for key,value in r.items():
                 val = val + "'{}',".format(format_sql(str(value)))
          print('val=',val)
          vals = vals +'({}),'.format(val[0:-1])

    print(desc + vals[0:-1])
    await async_processer.exec_sql(desc + vals[0:-1])


async def db_stru_compare(sour_db_server,sour_schema,desc_db_server,desc_schema):
      sds = await get_ds_by_dsid_by_cdb(sour_db_server,sour_schema)
      dds = await get_ds_by_dsid_by_cdb(desc_db_server,desc_schema)
      sql  = """SELECT  
                table_schema,
                table_name,
                column_name,
                is_nullable,
                data_type,
                column_default,
                character_maximum_length,
                numeric_precision,
                character_set_name,
                column_type,
                column_key,
                extra,
                column_comment
            FROM information_schema.columns 
            WHERE table_schema='{}' ORDER BY table_name,ordinal_position"""
      sres = await async_processer.query_dict_list_by_ds(sds,sql.format(sour_schema))
      dres = await async_processer.query_dict_list_by_ds(dds, sql.format(desc_schema))

      await async_processer.exec_sql('truncate table t_db_compare')
      await save_db(sour_db_server,sres)
      await save_db(desc_db_server,dres)

      sql = """
            SELECT a.table_schema,a.table_name,a.column_name,a.`is_nullable`,a.column_type
            FROM t_db_compare a
            WHERE dsid={} AND not exists(
                 select 1 FROM t_db_compare b
                    WHERE b.dsid={} 
                      AND b.`table_name`=a.`table_name`
                      AND b.`column_name`=a.`column_name`
                      AND b.`is_nullable` = a.`is_nullable`
                  AND b.`data_type` = a.`data_type`
                      AND b.`column_default` = a.`column_default`
                      AND b.`character_maximum_length` = a.`character_maximum_length`
                      AND b.`numeric_precision` = a.`numeric_precision`
                      AND b.`character_set_name` = a.`character_set_name`
                      AND b.`column_type` = a.`column_type`
                      AND b.`column_key` = a.`column_key`
                      AND b.`extra` = a.`extra`
                      AND b.`column_comment` = a.`column_comment`)
      """
      res = await async_processer.query_list(sql.format(sour_db_server,desc_db_server))
      return res