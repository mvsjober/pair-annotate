from django.conf.urls import url

from . import views

#------------------------------------------------------------------------------

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/', views.register, name='register'),
    url(r'^register_external/', views.register_external, name='register_external'),
    url(r'^annotate/', views.annotate, name='annotate')
]
