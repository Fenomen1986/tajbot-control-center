from django.urls import path
from .views import receive_lead
urlpatterns = [
    path('submit_lead/', receive_lead, name='submit_lead'),
]