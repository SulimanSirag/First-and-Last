#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Arvin
# datetime: 6/13/2019 5:40 PM
# software: PyCharm

from django.utils.translation import ugettext_lazy as _

from mysite.att.api.base_serializers import EmployeePayCodeRelatedReportModelSerializer
from mysite.att.api.filters import ReportGenericFilter
from mysite.att.api.utils_class import ReportUtilGenericViewSet
from mysite.att.api.utils_class import SumPayCodeDuration
from mysite.att.models import PayloadPayCode
from mysite.att.models.model_paycode import PayCode,OVERTIME
from rest_framework import serializers

def format_time(minutes):
    hours = minutes // 60
    minutes = minutes % 60
    days = hours // 7
    hours = hours % 7
    return "%d days: %02d H: %02d M" % (days, hours, minutes)


class EmployeeSummarySerializer(EmployeePayCodeRelatedReportModelSerializer):
    total_time=serializers.SerializerMethodField(label='Total Overtime',allow_null=True)

    def get_total_time(self,obj):
        return format_time(obj['total_time']) if obj['total_time'] else 0

    class Meta:
        model = PayloadPayCode
        fields = (
            'emp_id', 'emp_code', 'first_name', 'last_name', 'nick_name', 'gender', 'dept_name', 'dept_code',
            'position_code',
            'position_name','total_time'
        )


class EmployeeSummaryViewSet(ReportUtilGenericViewSet):
    model = PayloadPayCode
    queryset = PayloadPayCode.objects.all().select_related()
    filter_class = ReportGenericFilter

    serializer_dict = {
        'list': EmployeeSummarySerializer,
        'export': EmployeeSummarySerializer,
    }

    @property
    def pay_codes(self):
        if not hasattr(self, '_pay_codes'):
            self._pay_codes = PayCode.objects.all().order_by('display_order').values(
                'id', 'name', 'display_format', 'min_val', 'round_off')
        return self._pay_codes

    def get_file_title(self):
        return _("menu_att_employeeSummaryReport")

    def annotate_queryset(self, queryset):
        queryset = queryset.values(
            'emp_id', 'emp__emp_code', 'emp__first_name', 'emp__last_name', 'emp__nickname', 'emp__gender',
            'emp__department__dept_code', 'emp__department__dept_name', 'emp__position__position_code',
            'emp__position__position_name'
        ).order_by('emp__emp_code')
        values={}
        from mysite.att import const
        from django.db.models import Sum,Case,Value,When,IntegerField
        if self.pay_codes:

            for pay_code in self.pay_codes:
                self.summary_fields.append('paycode_{index}'.format(index=pay_code['id']))
                values['paycode_{index}'.format(index=pay_code['id'])] = SumPayCodeDuration(pay_code)

            self.summary_fields.append('total_time')
            values['total_time'] = Sum(Case(When(pay_code__code_type=OVERTIME,then='minutes'),default=0),output_field=IntegerField())
            queryset = queryset.annotate(**values)


        return queryset
