import json

from django import http
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator

from ostinato.views import JsonResponseMixin
from ostinato.statemachine import InvalidTransition


class StateActionView(JsonResponseMixin, View):
    """
    This updates the state for an object.
    If the request is ajax, we will return json, if not, we will redirect
    to the next url specified in the post arguments.
    """
    def put(self, *args, **kwargs):
        context = {}
        data = json.loads(self.request.read())

        # Based on the action we need to check the permissions and act
        # accordingly
        perm_codename = "can_%s_%s" % (data['action'], kwargs['model'])
        if not self.request.user.has_perm('%s.%s' % (kwargs['app_label'], perm_codename)):
            return http.HttpResponseForbidden()

        # Import the statemachine
        module_path, sm_class = data['statemachine'].rsplit('.', 1)
        StateMachine = __import__(
            module_path, locals(), globals(), [sm_class], -1
        ).__dict__[sm_class]

        # Get the object model instance
        model_type = ContentType.objects.get(
            app_label=kwargs['app_label'], model=kwargs['model'])
        obj = model_type.get_object_for_this_type(id=kwargs['obj_id'])

        sm = StateMachine(obj)
        try:
            sm.take_action(data['action'])
        except InvalidTransition, e:
            return http.HttpResponseForbidden(e)
        obj.save()

        return self.render_json_response(context)
