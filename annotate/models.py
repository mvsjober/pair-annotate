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
from django.db import models
from django_countries.fields import CountryField

import numpy as np

#------------------------------------------------------------------------------
    
class Video(models.Model):
    filename = models.CharField(max_length=200)
    # comma-separated list of p values, 10 chars * max 5000 values
    p_values = models.TextField(max_length=5000, default="", blank=True)
    number = models.IntegerField()

    # how many rounds of annotation-BTL-calculation have been done
    annotation_rounds = models.IntegerField(default=0)

    # status
    ANNOTATING = 0
    CALCULATING = 1
    
    status = models.IntegerField(default=ANNOTATING)

    def __str__(self):
        return '[{}] {}'.format(self.number, self.filename)

    def get_p_values(self):
        if self.p_values is None or self.p_values == "":
            return None
        return np.array([float(x) for x in self.p_values.split(',')])

    def set_p_values(self, p):
        self.p_values = ','.join([str(x) for x in p])
            

#------------------------------------------------------------------------------

class Shot(models.Model):
    video = models.ForeignKey(Video)
    filename = models.CharField(max_length=200)
    number = models.IntegerField()
    image_filename = models.CharField(max_length=200)

    def __str__(self):
        return '[{}:{}] {}'.format(self.video.number, self.number, 
                                    self.filename)

#------------------------------------------------------------------------------

class ShotPair(models.Model):
    video = models.ForeignKey(Video)
    shot_1 = models.ForeignKey(Shot, related_name='+')
    shot_2 = models.ForeignKey(Shot, related_name='+')
    annotation_started = models.DateTimeField(null=True)

    # status
    UNANNOTATED = 0
    SHOT_1_SELECTED = 1
    SHOT_2_SELECTED = 2
    RESERVED = -1
    
    status = models.IntegerField(default=UNANNOTATED)

    def __str__(self):
        return '{}: {} vs {} - Status: {}'.format(self.video.number,
                                                  self.shot_1.number,
                                                  self.shot_2.number,
                                                  self.status)

#------------------------------------------------------------------------------

class Annotator(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    last_video = models.ForeignKey(Video, null=True)
    age = models.PositiveSmallIntegerField(null=True)
    gender = models.CharField(max_length=10, null=True, choices=(
        ("male", "Male"),
        ("female", "Female"),
        ("another", "Another/prefer not to disclose")))
    country = CountryField(null=True)
    annotation_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Annotator: " + self.user.username

#------------------------------------------------------------------------------

class LogAnnotation(models.Model):
    annotator = models.ForeignKey(Annotator)

    video = models.ForeignKey(Video, related_name='+')
    shot_1 = models.ForeignKey(Shot, related_name='+')
    shot_2 = models.ForeignKey(Shot, related_name='+')

    vote = models.IntegerField(default=ShotPair.UNANNOTATED)
    annotation_round = models.IntegerField(default=0)
    when = models.DateTimeField(null=True)

    cheat = models.BooleanField(default=False)

    def __str__(self):
        return '{}: {}, video {} round {}: {} vs {} - vote {}'.format(
            self.when,
            self.annotator.user.username, self.video.number, self.annotation_round,
            self.shot_1.number, self.shot_2.number, self.vote)

#------------------------------------------------------------------------------

class LogRanking(models.Model):
    video = models.ForeignKey(Video, related_name='+')
    annotation_round = models.IntegerField(default=0)
    when = models.DateTimeField(null=True)
    p_values = models.TextField(max_length=5000, default="", blank=True)
