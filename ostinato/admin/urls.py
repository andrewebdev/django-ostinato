from django.urls import path
from .views import OstinatoEditorView


urlpatterns = [
    path(
        'editor-frame/',
        OstinatoEditorView.as_view(),
        name="ostinato_admin_editor_frame"),
]
