from django.contrib import admin
from django import forms
from .models import Setting


class SettingForm(forms.ModelForm):
    class Meta:
        model = Setting
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ftype = self.instance.value_type

        if ftype in ['int', 'dec']:
            widget = forms.NumberInput()
        elif ftype == 'boolean':
            widget = forms.CheckboxInput()
        else:
            widget = forms.TextInput()

        self.fields['setting_key'].disabled = True
        self.fields['value_type'].disabled = True
        self.fields['setting_value'].widget = widget


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    form = SettingForm
    search_fields = ('setting_key', 'setting_value')
    list_display = (
        'detail_link',
        'setting_key',
        'value_type',
        'setting_value')
    list_editable = ('setting_key', 'value_type', 'setting_value')

    def detail_link(self, obj):
        return "Detail"

    def get_changelist_form(self, request, **kwargs):
        return SettingForm

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False
