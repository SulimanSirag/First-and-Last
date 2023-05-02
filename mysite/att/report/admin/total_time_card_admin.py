#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Arvin
# datetime: 1/26/2021 10:29 AM
# software: BioTime
from mysite.att.report.base import ReportAdminBase
from mysite.att.report.decorators import report_register
from mysite.att.report import const
from mysite.att.api.report_views import PayloadTimeCardViewSet
from mysite.att.api.report_views.total_timecard import PayloadTimeCardSerializer


@report_register()
class TotalTimeCardAdmin(ReportAdminBase):
    model_name = 'totalTimeCardReportV2'
    view_name = 'total_time_card_v2'
    template = 'att/report_new/total_time_card_v2.html'
    data_source = '/att/api/totalTimeCardReportV2/'
    api_view = PayloadTimeCardViewSet
    serializer = PayloadTimeCardSerializer
    list_display = (
        'emp_code', 'first_name', 'last_name', 'nick_name', 'gender', 'dept_code', 'dept_name', 'position_code',
        'position_name', 'att_date', 'weekday', 'time_table_alias', 'check_in', 'check_out', 'duty_duration',
        'break_duration', 'work_day', 'clock_in', 'clock_out', 'total_hrs', 'worked_hrs', 'break_out', 'break_in',
        'break_total_hrs', 'break_hrs', 'total_ot', 'rule_total_ot', 'total_leave','day_off','weekend','holiday', 'approval_hrs', 'unschedule',
        'remaining','device_in','device_out','work_code_in','work_code_out','gps_in','gps_out','exception'
    )
    hidden_fields = ('last_name', 'nick_name', 'gender', 'dept_code', 'position_code', 'position_name','device_in','device_out','work_code_in','work_code_out','gps_in','gps_out')
    sort_fields = ('emp_code', 'att_date')

    def get_layui_cols(self):
        from mysite.att.models import PayCode
        cols = super(TotalTimeCardAdmin, self).get_layui_cols()
        codes = PayCode.objects.all().order_by('display_order').values('id', 'name', 'is_display')
        for code in codes:
            cols.append({'field': 'paycode_{0}'.format(code['id']), 'title': code['name'],
                         'hide': self.bool_value(not code['is_display'])})
            cols.append({'field':'exception','title':'Exception Type','hide':self.bool_value(False)})
        return cols
