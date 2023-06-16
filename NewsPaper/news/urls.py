from django.urls import path
from .views import NewsList, NewsDetail, NewsCreate, NewsDelete, NewsUpdate, NewsSearch, subscribe

urlpatterns = [
    path("", NewsList.as_view()),
    path('<int:pk>', NewsDetail.as_view()),
    path('add/', NewsCreate.as_view()),
    path('<int:pk>/delete', NewsDelete.as_view(), name='news_delete'),
    path('<int:pk>/edit', NewsUpdate.as_view(), name='news_update'),
    path('search/', NewsSearch.as_view()),
    path('subscribe', subscribe, name='subscribe')
]
