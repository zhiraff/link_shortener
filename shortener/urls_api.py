from django.urls import path, include
from .views import CreateSingleLinkView, GetSingleLinkView

urlpatterns = [
    path("", CreateSingleLinkView.as_view(), name='create_single_link'),
    path("<slug:slug>/", GetSingleLinkView.as_view(), name='get_single_link'),
]
