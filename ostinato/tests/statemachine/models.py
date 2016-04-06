from django.db import models

from .workflow import TestStateMachine


class TestModel(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=20, null=True, blank=True)
    state_num = models.IntegerField(null=True, blank=True)
    other_state = models.CharField(max_length=20, null=True, blank=True)
    message = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        permissions = TestStateMachine.get_permissions('testmodel', 'Test')

