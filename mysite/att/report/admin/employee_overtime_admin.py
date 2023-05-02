#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Bosco
# datetime: 1/27/2021 4:17 PM
# software: BioTime

from mysite.att.report.base import ReportAdminBase
from mysite.att.report.decorators import report_register
from mysite.att.api.report_views import EmployeeOvertimeViewSet
from mysite.att.api.report_views.employee_overtime import EmployeeOvertimeSerializer


@report_register()
class EmployeeOvertimeAdmin(ReportAdminBase):
    model_name = 'employeeOvertimeReport'
    view_name = 'employee_overtime'
    template = 'att/report_new/employee_overtime.html'
    api_view = EmployeeOvertimeViewSet
    serializer = EmployeeOvertimeSerializer
    data_source = '/att/api/employeeOvertimeReport/'
    list_display = (
        'emp_code', 'first_name', 'last_name', 'nick_name', 'gender', 'dept_code', 'dept_name',
        'position_code', 'position_name','total_time'
    )
    hidden_fields = ('last_name', 'nick_name', 'gender', 'dept_code', 'position_code', 'position_name')
    sort_fields = ('emp_code')

    def get_layui_cols(self):
        from mysite.att.models.model_paycode import PayCode, OVERTIME
        cols = super(EmployeeOvertimeAdmin, self).get_layui_cols()
        codes = PayCode.objects.filter(
            code_type=OVERTIME).order_by('display_order').values('id', 'name', 'is_display')
        for code in codes:
            cols.append({'field': 'paycode_{0}'.format(code['id']), 'title': code['name'],
                         'hide': self.bool_value(not code['is_display'])})
            cols.append({'field':'total_time','title':'Total OT','hide':self.bool_value(False)})
        return cols
