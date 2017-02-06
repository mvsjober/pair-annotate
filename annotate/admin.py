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

from django.contrib import admin

from .models import *

class AnnotatorAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'annotation_count', 'country')

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = 'Username'

class VideoAdmin(admin.ModelAdmin):
    list_display = ('filename', 'number', 'status', 'annotation_rounds')

class ShotAdmin(admin.ModelAdmin):
    list_display = ('filename', 'number', 'video')

class ShotPairAdmin(admin.ModelAdmin):
    list_display = ('status', 'annotation_started', 'shot_1', 'shot_2', 'video')

class LogRankingAdmin(admin.ModelAdmin):
    list_display = ('video', 'annotation_round', 'when')

class LogAnnotationAdmin(admin.ModelAdmin):
    list_display = ('video', 'shot_1', 'shot_2', 'annotation_round', 'vote', 'when')

admin.site.register(Video, VideoAdmin)
admin.site.register(Shot, ShotAdmin)
admin.site.register(ShotPair, ShotPairAdmin)
admin.site.register(Annotator, AnnotatorAdmin)

admin.site.register(LogAnnotation, LogAnnotationAdmin)
admin.site.register(LogRanking, LogRankingAdmin)
