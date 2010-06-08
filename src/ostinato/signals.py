from django.dispatch import Signal

post_action_publish = Signal()
post_action_review = Signal()
post_action_hide = Signal()
post_action_draft = Signal()
