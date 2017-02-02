#!/usr/bin/env python3

from django.core.management.base import BaseCommand
from annotate.models import Annotator

class Command(BaseCommand):
    args = ''
    help = 'Reset annotation counts for all users'

    def _reset_counts(self):
        for annotator in Annotator.objects.all():
            annotator.annotation_count = 0
            print('Setting count for {} = {}'.format(annotator.user.username,
                                                     annotator.annotation_count))
            annotator.save()

    def handle(self, *args, **options):
        self._reset_counts()
