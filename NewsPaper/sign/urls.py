from django.urls import path
from .views import AccountOptions, authorise

urlpatterns = [
    path('options/', AccountOptions.as_view(), name="options"),
    path('authorisation/', authorise, name="authorise")
]
