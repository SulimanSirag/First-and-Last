#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Arvin
# datetime: 4/2/2020 8:37 PM
# software: BioTime
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response

from mysite.api.serializers.utils import EmployeeExtraInfoSerializer
from mysite.att.api import fields
from mysite.att.api.base_serializers import PayCodeRelatedReportModelSerializer
from mysite.att.api.filters import ReportGenericFilter
from mysite.att.api.utils_class import ReportUtilGenericViewSet
from mysite.att.api.utils_class import SumPayCodeDuration, SumAttCodeDuration
from mysite.att.models import PayloadTimeCard, PayCode, AttCode
from mysite.att.models import PayloadPayCode
from mysite.att import const 

class PayloadTimeCardSerializer(PayCodeRelatedReportModelSerializer, EmployeeExtraInfoSerializer):
    emp_code = serializers.CharField(label=_('report_column_empCode'), source='emp__emp_code')
    first_name = serializers.CharField(label=_('report_column_firstName'), source='emp__first_name', allow_null=True)
    last_name = serializers.CharField(label=_('report_column_lastName'), source='emp__last_name', allow_null=True)
    nick_name = serializers.CharField(label=_('report_column_nickName'), source='emp__nickname', allow_null=True)
    gender = serializers.CharField(label=_('report_column_gender'), source='emp__gender', allow_null=True)
    dept_code = serializers.CharField(
        label=_('report_column_departmentCode'), source='emp__department__dept_code', allow_null=True)
    dept_name = serializers.CharField(
        label=_('report_column_departmentName'), source='emp__department__dept_name', allow_null=True)
    position_code = serializers.CharField(
        label=_('report_column_positionCode'), source='emp__position__position_code', allow_null=True)
    position_name = serializers.CharField(
        label=_('report_column_positionName'), source='emp__position__position_name', allow_null=True)
    att_date = fields.DateField(label=_('report_column_attendanceDate'))
    time_table_alias = serializers.SerializerMethodField(label=_('report.columns.timetable'))
    check_in = fields.TimeField(label=_('report.columns.checkIn'))
    check_out = fields.TimeField(label=_('report.columns.checkOut'))
    clock_in = fields.TimeField(label=_('report.columns.clockIn'))
    clock_out = fields.TimeField(label=_('report.columns.clockOut'))
    break_in = fields.TimeField(label=_('report.columns.breakIn'))
    break_out = fields.TimeField(label=_('report.columns.breakOut'))
    weekday = fields.WeekdayField(label=_('report_column_attendanceWeekday'))
    att_date_normal = serializers.DateField(source='att_date')
    device_in = serializers.SerializerMethodField(label=_('report_column_deviceTn'))
    device_out = serializers.SerializerMethodField(label=_('report_column_deviceOut'))
    work_code_in = serializers.SerializerMethodField(label=_('report_column_workCodeIn'))
    work_code_out = serializers.SerializerMethodField(label=_('report_column_workCodeOut'))
    gps_in = serializers.SerializerMethodField(label=_('report_column_locationIn'))
    gps_out = serializers.SerializerMethodField(label=_('report_column_locationOut'))
    exception = serializers.SerializerMethodField(label=_('report_column_exception'))
    colorful = True
    
    
    def get_exception(self, obj):
        id_str = str(obj['id'])
        try:
            import uuid
            time_card_id = uuid.UUID(id_str)
            pay_codes = PayloadPayCode.objects.filter(time_card_id=time_card_id, pay_code__code_type=const.LEAVE)
            pay_code_alias = pay_codes.values('pay_code_alias').first()
            if pay_code_alias:
                return pay_code_alias.get('pay_code_alias', '')
            
        except Exception as e:
            return ''

    
    def get_work_code_in(self,obj):
        from mysite.iclock.models import Transaction
        clockin = obj.get('clock_in')
        emp_code = obj.get('emp__emp_code')
        if clockin:
            transdata = Transaction.objects.filter(punch_time=clockin,emp_code=emp_code).first()
            if transdata:
                return transdata.work_code
            else:
                return " "
        else:
            return " "

    def get_work_code_out(self, obj):
        from mysite.iclock.models import Transaction
        clockout = obj.get('clock_out')
        emp_code = obj.get('emp__emp_code')
        if clockout:
            transdata = Transaction.objects.filter(punch_time=clockout,emp_code=emp_code).first()
            if transdata:
                return transdata.work_code
            else:
                return " "
        else:
            return " "


    def get_device_in(self,obj):
        from mysite.iclock.models import Transaction
        clockin = obj.get('clock_in')
        emp_code = obj.get('emp__emp_code')
        if clockin:
            transdata = Transaction.objects.filter(punch_time=clockin,emp_code=emp_code).first()
            if transdata:
                return transdata.terminal_alias
            else:
                return ""
        else:
            return ""

    def get_device_out(self,obj):
        from mysite.iclock.models import Transaction
        clockout = obj.get('clock_out')
        emp_code = obj.get('emp__emp_code')
        if clockout:
            transdata = Transaction.objects.filter(punch_time=clockout,emp_code=emp_code).first()
            if transdata:
                return transdata.terminal_alias
            else:
                return ""
        else:
            return " "

    def get_time_table_alias(self, obj):
        color = obj.get('time_table__color_setting', None)
        alias = obj.get('time_table_alias', '')
        if not color:
            return alias
        return format_html('<div style="color:#ffffff;background:{0}">{1}</div>', color, alias)

    def get_fields(self):
        fields = super(PayloadTimeCardSerializer, self).get_fields()
        self.add_emp_extra_info_fields(fields)
        return fields

    def get_gps_in(self,obj):
        from mysite.iclock.models import Transaction
        clockin  = obj.get('clock_in')
        emp_code = obj.get('emp__emp_code')
        if clockin:
            transdata = Transaction.objects.filter(punch_time=clockin,emp_code=emp_code).first()
            print(transdata.gps_location)
            if transdata:
                return transdata.gps_location
            else:
                return " "
        else:
            return " "

    def get_gps_out(self,obj):
        from mysite.iclock.models import Transaction
        clockout = obj.get('clock_out')
        if clockout:
            transdata = Transaction.objects.filter(punch_time=clockout).first()
            if transdata:
                return transdata.gps_location
            else:
                return ""
        else:
            return " "

    class Meta:
        model = PayloadTimeCard
        fields = (
            'id', 'emp_id', 'emp_code', 'first_name', 'last_name', 'nick_name', 'gender', 'dept_code', 'dept_name',
            'position_code', 'position_name', 'att_date', 'weekday', 'time_table_alias',
            'check_in', 'check_out', 'work_day', 'clock_in', 'clock_out',
            'break_out', 'break_in', 'att_date_normal', 'time_table_id', 'device_in', 'device_out','work_code_in', 'work_code_out','gps_in',
            'gps_out','exception')


class PayloadTimeCardFilter(ReportGenericFilter):

    class Meta:
        model = PayloadTimeCard
        fields = ['employees', 'departments', 'start_date', 'end_date']


class PayloadTimeCardViewSet(ReportUtilGenericViewSet):
    model = PayloadTimeCard
    queryset = PayloadTimeCard.objects.select_related().order_by(
        'emp', 'att_date', 'clock_in')
    filter_class = PayloadTimeCardFilter

    serializer_dict = {
        'list': PayloadTimeCardSerializer,
        'export': PayloadTimeCardSerializer,
    }

    @property
    def att_codes(self):
        if not hasattr(self, '_att_codes'):
            self._att_codes = AttCode.objects.order_by('order').values('id', 'code', 'alias', 'display_format', 'min_val', 'round_off', 'color_setting')
        return self._att_codes

    @property
    def pay_codes(self):
        if not hasattr(self, '_pay_codes'):
            self._pay_codes = PayCode.objects.filter(is_display=True).order_by('display_order').values(
                'id', 'name', 'display_format', 'min_val', 'round_off', 'color_setting')
        return self._pay_codes

    def annotate_queryset(self, queryset):
        queryset = queryset.values(
            'id', 'emp_id', 'emp__emp_code', 'emp__first_name', 'emp__last_name', 'emp__nickname', 'emp__gender',
            'emp__department__dept_code', 'emp__department__dept_name', 'emp__position__position_code',
            'emp__position__position_name', 'time_table_alias', 'att_date', 'week', 'weekday', 'check_in', 'check_out',
            'clock_in', 'clock_out', 'break_out', 'break_in', 'work_day', 'time_table__color_setting', 'time_table_id'
        ).order_by('emp__emp_code', 'att_date', 'clock_in')
        values = {}
        if self.att_codes:
            for att_code in self.att_codes:
                self.summary_fields.append(att_code['code'])
                values[att_code['code']] = SumAttCodeDuration(
                    att_code, fk='payloadattcode', distinct=True)
        if self.pay_codes:
            for pay_code in self.pay_codes:
                self.summary_fields.append('paycode_{index}'.format(index=pay_code['id']))
                values['paycode_{0}'.format(pay_code['id'])] = SumPayCodeDuration(
                    pay_code, fk='payloadpaycode', distinct=True)
        if values:
            queryset = queryset.annotate(**values)
        return queryset

    def get_file_title(self):
        return _("att.menus.reports.totalTimeCard")

    @action(methods=['get'], detail=False, renderer_classes=[JSONRenderer, TemplateHTMLRenderer])
    def view_att_setting_form(self, request, *args, **kwargs):
        from mysite.att.forms.view_att_setting_forms import AttSettingViewForm
        if request.method.lower() == 'get':
            return Response({'form': AttSettingViewForm(request)},
                            template_name='att/view_att_setting.html')
        else:
            return Response({'code': 1, 'message': 'Invalid Action'}, status=400)
