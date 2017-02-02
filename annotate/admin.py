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

admin.site.register(Video, VideoAdmin)
admin.site.register(Shot, ShotAdmin)
admin.site.register(ShotPair, ShotPairAdmin)
admin.site.register(Annotator, AnnotatorAdmin)

