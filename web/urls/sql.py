#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2020/12/5 12:33
# @Author : ma.fei
# @File : logon.py.py
# @Software: PyCharm

from web.services.sql    import sqlquery,sql_query,sqlrelease,sql_check,sql_format,sql_check_result
from web.services.sql    import sql_release,sqlaudit,sql_audit,sqlrun,sql_run,sql_audit_query,sql_audit_detail,sql_run_query
from web.services.sql    import get_tree_by_sql,query_sql_release,sql_detail,sql_exp_xls,sql_exp_pdf,sql_rollback_exp
from web.services.sql    import sql_exp_query,_sql_exp_query,_sql_exp_save,_sql_exp_update,_sql_exp_delete,_sql_exp_audit,_sql_exp_export

sql = [
        (r"/sql/query", sqlquery),
        (r"/sql/_query", sql_query),
        (r"/sql/detail", sql_detail),
        (r"/sql/release", sqlrelease),
        (r"/sql/_release", sql_release),
        (r"/sql/_check", sql_check),
        (r"/sql/_check/result", sql_check_result),
        (r"/sql/audit", sqlaudit),
        (r"/sql/_audit", sql_audit),
        (r"/sql/audit/query", sql_audit_query),
        (r"/sql/audit/detail", sql_audit_detail),
        (r"/sql/_format", sql_format),
        (r"/sql/run", sqlrun),
        (r"/sql/_run", sql_run),
        (r"/get/sql/release", query_sql_release),
        (r"/sql/run/query", sql_run_query),
        (r"/get_tree", get_tree_by_sql),
        (r"/sql/export/excel", sql_exp_xls),
        (r"/sql/export/pdf", sql_exp_pdf),
        (r"/sql/rollback/export", sql_rollback_exp),
        (r"/sql/exp/query", sql_exp_query),
        (r"/sql/exp/_query", _sql_exp_query),
        (r"/sql/exp/_save", _sql_exp_save),
        (r"/sql/exp/_update", _sql_exp_update),
        (r"/sql/exp/_delete", _sql_exp_delete),
        (r"/sql/exp/_audit", _sql_exp_audit),
        (r"/sql/exp/_export", _sql_exp_export),


]