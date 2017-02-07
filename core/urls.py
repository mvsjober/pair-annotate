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

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout

app_path = settings.MY_APP_PATH

urlpatterns = [
    # annotate is the root
    url(r'^' + app_path,
        include('annotate.urls', namespace='annotate')),
    # User account handling
    url(r'^' + app_path + 'accounts/login/$',  login, {'extra_context': {'modality': settings.MEDIAEVAL_MODALITY}}),
    url(r'^' + app_path + 'accounts/logout/$', logout, {'extra_context': {'modality': settings.MEDIAEVAL_MODALITY}}),
    # admin
    url(r'^' + app_path + 'admin/', admin.site.urls),
    # social login
    url(r'^' + app_path,
        include('social_django.urls', namespace='social')),
]
