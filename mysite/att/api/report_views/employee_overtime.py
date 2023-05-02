#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Arvin
# datetime: 4/3/2020 4:22 PM
# software: BioTime
from django.utils.translation import ugettext_lazy as _

from mysite.att.api.base_serializers import EmployeePayCodeRelatedReportModelSerializer
from mysite.att.api.filters import ReportGenericFilter
from mysite.att.api.utils_class import ReportUtilGenericViewSet
from mysite.att.api.utils_class import SumPayCodeDuration
from mysite.att.models import PayloadPayCode
from mysite.att.models.model_paycode import PayCode, OVERTIME
from rest_framework import serializers

# def format_time(minutes):
#     hours=minutes // 60
#     minutes = minutes % 60
#     return "%02d:%02d" % (hours, minutes)

def format_time(minutes):
    hours = minutes // 60
    minutes = minutes % 60
    days = hours // 7
    hours = hours % 7
    return "%d days: %02d H: %02d M" % (days, hours, minutes)


class EmployeeOvertimeSerializer(EmployeePayCodeRelatedReportModelSerializer):
    total_time=serializers.SerializerMethodField(label='Total Overtime',allow_null=True)

    def get_total_time(self,obj):
        return format_time(obj['total_time']) if obj['total_time'] else 0

    class Meta:
        model = PayloadPayCode
        fields = (
            'id', 'emp_id', 'emp_code', 'first_name', 'last_name', 'nick_name', 'gender', 'dept_code', 'dept_name',
            'position_code', 'position_name','total_time')


class EmployeeOvertimeFilter(ReportGenericFilter):

    class Meta:
        model = PayloadPayCode
        fields = ['employees', 'departments', 'start_date', 'end_date']


class EmployeeOvertimeViewSet(ReportUtilGenericViewSet):
    model = PayloadPayCode
    queryset = PayloadPayCode.objects.filter(pay_code__code_type=OVERTIME).filter(duration__gt=0)
    filter_class = EmployeeOvertimeFilter
    serializer_dict = {
        'list': EmployeeOvertimeSerializer,
        'export': EmployeeOvertimeSerializer,
    }

    @property
    def pay_codes(self):
        if not hasattr(self, '_pay_codes'):
            self._pay_codes = PayCode.objects.filter(
                code_type=OVERTIME).order_by('display_order').values(
                'id', 'name', 'display_format', 'min_val', 'round_off')
        return self._pay_codes

    def annotate_queryset(self, queryset):
        queryset = queryset.values(
            'emp_id', 'emp__emp_code', 'emp__first_name', 'emp__last_name', 'emp__nickname', 'emp__gender',
            'emp__department__dept_code', 'emp__department__dept_name', 'emp__position__position_code',
            'emp__position__position_name'
        ).order_by('emp__emp_code')
        from django.db.models import Sum
        if self.pay_codes:
            values = {}
            for pay_code in self.pay_codes:
                self.summary_fields.append('paycode_{index}'.format(index=pay_code['id']))
                values['paycode_{index}'.format(index=pay_code['id'])] = SumPayCodeDuration(pay_code)
            values['total_time']=Sum('minutes')
            self.summary_fields.append('total_time')
            queryset = queryset.annotate(**values)
        return queryset

    def get_file_title(self):
        return _("att.menus.reports.employeeOvertime")
