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
        """
            We expect the following JSON data to be sent to this view:
            {
                "statemachine": "<import path to statemachine class>",
                "action": "<action codeword to be taken>",
                "next": "<next url to redirect to if request is not ajax>",
                "action_kwargs": <kwargs dict passed to the action method>,
            }

            Returns Json:
            {
                "status": "ok",
                "state_before": "<state before action taken>",
                "state_after": "<state after action taken>",
                "action_taken": "<action that was taken>",
            }
        """
        data = json.loads(self.request.read())
        action_kwargs = data.get('action_kwargs', {})

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
        state_before = sm.state
        try:
            sm.take_action(data['action'], **action_kwargs)
        except InvalidTransition, e:
            return http.HttpResponseForbidden(e)
        state_after = sm.state
        obj.save()

        if self.request.is_ajax():
            return self.render_json_response({
                "status": "ok",
                "state_before": state_before,
                "state_after": state_after,
                "action_taken": data['action'],
            })
        else:
            return http.HttpResponseRedirect(data['next'])
