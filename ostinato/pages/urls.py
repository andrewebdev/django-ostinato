from django.urls import path
from ostinato.pages.views import (
    page_dispatch,
    PageReorderView,
    PageDuplicateView
)


urlpatterns = [
    path('', page_dispatch, name='ostinato_page_home'),

    path(
        'page_reorder/',
        PageReorderView.as_view(),
        name='ostinato_page_reorder'
    ),

    path(
        'page_duplicate/',
        PageDuplicateView.as_view(),
        name='ostinato_page_duplicate'
    ),

    # This must be last
    path('<path:path>', page_dispatch, name='ostinato_page_view'),
]
