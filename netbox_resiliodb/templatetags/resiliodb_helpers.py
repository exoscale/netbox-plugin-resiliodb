from django import template
from django.contrib.contenttypes.models import ContentType
from netbox_resiliodb.models import LCAParams

register = template.Library()

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
