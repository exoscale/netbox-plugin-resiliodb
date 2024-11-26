from django import template
from django.contrib.contenttypes.models import ContentType
from netbox_resiliodb.models import LCAParams
from django.utils.html import format_html
import json

register = template.Library()

@register.filter
def render_json_as_table(json_data):
    """Renders a JSON object as an HTML table"""
    if not json_data:
        return ''
    
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except:
            return json_data
            
    def render_value(value):
        if isinstance(value, dict):
            return render_dict_as_table(value)
        elif isinstance(value, (list, tuple)):
            return render_list_as_table(value)
        else:
            return str(value)
            
    def render_dict_as_table(d):
        rows = []
        for key, value in d.items():
            formatted_value = render_value(value)
            rows.append(f'<tr><th class="text-start">{key}</th><td>{formatted_value}</td></tr>')
        return format_html('<table class="table table-hover">{}</table>', format_html(''.join(rows)))
        
    def render_list_as_table(lst):
        rows = []
        for i, value in enumerate(lst):
            formatted_value = render_value(value)
            rows.append(f'<tr><th class="text-start">{i}</th><td>{formatted_value}</td></tr>')
        return format_html('<table class="table table-hover">{}</table>', format_html(''.join(rows)))
        
    return render_value(json_data)

@register.filter
def multiply(value, arg):
    """Multiply the arg by the value"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def content_type_parameters(obj):
    """
    Returns LCAParams for a given object using content type lookup
    """
    content_type = ContentType.objects.get_for_model(obj)
    return LCAParams.objects.filter(
        content_type=content_type,
        object_id=obj.pk
    ).first()
