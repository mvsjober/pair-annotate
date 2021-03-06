#------------------------------------------------------------------------------
#  Copyright (c) 2017 University of Helsinki
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------

from django.conf.urls import url

from . import views

#------------------------------------------------------------------------------

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/', views.register, name='register'),
    url(r'^register_external/', views.register_external, name='register_external'),
    url(r'^annotate/', views.annotate, name='annotate'),
    url(r'^cheat/', views.cheat, name='cheat'),
    url(r'^status/$', views.status, name='status'),
    url(r'^status/log/', views.log, name='log'),
    url(r'^status/annotators/', views.annotators, name='annotators')
]
