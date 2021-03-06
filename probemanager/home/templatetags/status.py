import importlib
import logging

from django import template

from home.models import Probe

logger = logging.getLogger(__name__)
register = template.Library()


@register.filter
def status(probe_id):
    probe = Probe.get_by_id(probe_id)
    if probe is None:  # pragma: no cover
        return {"message": "Error - probe is None - param id not set : " + str(probe_id)}
    if probe.subtype:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.subtype)
    else:
        my_class = getattr(importlib.import_module(probe.type.lower() + ".models"), probe.type)
    probe = my_class.get_by_id(probe_id)
    response = probe.status()
    if 'active (running)' in response:
        return 'success'
    else:
        return 'danger'
