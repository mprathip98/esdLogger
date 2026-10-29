from django.urls import path
from . import views
from django.conf import settings # Import settings
from django.conf.urls.static import static



#for navigating into each page
urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('retrieve/', views.retrieve, name='retrieve'),
    path('retrieve_pdf/', views.retrieve_pdf, name='retrieve_pdf'),
    path('verify/', views.verify, name='verify'),

]
