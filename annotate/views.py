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


from annotate.models import Video, Annotator, ShotPair, LogAnnotation, Shot

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Case, When, IntegerField, Q
from django.core.mail import send_mail

import logging
import math
import os
import random

from itertools import groupby, count

#------------------------------------------------------------------------------

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------

class AnnotatorForm(ModelForm):
    class Meta:
        model = Annotator
        fields = ['age', 'gender', 'country']

#------------------------------------------------------------------------------

def register(request):
    error = None
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        annotator_form = AnnotatorForm(request.POST)

        if request.POST['secret'] != settings.REGISTER_SECRET:
            error = 'Secret is wrong!'
            
        if user_form.is_valid() and annotator_form.is_valid() and error == None:
            new_user = user_form.save()

            new_annotator = annotator_form.save(commit=False)
            new_annotator.user = new_user
            new_annotator.save()
            
            return HttpResponseRedirect('/' + settings.MY_APP_PATH)
    else:
        user_form = UserCreationForm()
        annotator_form = AnnotatorForm()

    return render(request, "registration/register.html", {
        'modality': settings.MEDIAEVAL_MODALITY,
        'user_form': user_form,
        'annotator_form': annotator_form,
        'error': error,
    })

#------------------------------------------------------------------------------

def register_external(request):
    error = None
    if request.method == 'POST':
        annotator_form = AnnotatorForm(request.POST)

        if request.POST['secret'] != settings.REGISTER_SECRET:
            error = 'Secret is wrong!'
            
        if annotator_form.is_valid() and error == None:
            new_annotator = annotator_form.save(commit=False)
            new_annotator.user = request.user
            new_annotator.save()
            
            return HttpResponseRedirect('/' + settings.MY_APP_PATH)
    else:
        annotator_form = AnnotatorForm()

    return render(request, "registration/register_external.html", {
        'modality': settings.MEDIAEVAL_MODALITY,
        'annotator_form': annotator_form,
        'error': error,
    })

#------------------------------------------------------------------------------

def get_annotator(user):
    """"Returns the annotator object associated with this user.

    A new annotator is created if no object exists.

    """

    # first ensure we have found the videos to annotate
    # if len(VIDEOS) == 0:
    #     raise Exception("Unable to find videos")

    annotator = None
    try:
        annotator = Annotator.objects.get(user=user)
    except Annotator.DoesNotExist:
        pass

    return annotator

#------------------------------------------------------------------------------

@login_required
def index(request):
    annotator = get_annotator(request.user)

    if annotator is None:
        return HttpResponseRedirect(reverse('annotate:register_external'))

    annotation_count = LogAnnotation.objects.filter(annotator=annotator, cheat=False).count()
    
    return render(request, 'annotate/index.html', 
                  { 'annotation_count': annotation_count,
                    'modality': settings.MEDIAEVAL_MODALITY})


#------------------------------------------------------------------------------

def cheat(request):
    return render(request, 'annotate/cheat.html', 
                  { 'modality': settings.MEDIAEVAL_MODALITY})

#------------------------------------------------------------------------------

def kick_out(username):
    from django.contrib.sessions.models import Session
    from django.contrib.auth.models import User

    user = User.objects.get(username=username)
    print(user, username, user.id)

    for s in Session.objects.all():
        if str(s.get_decoded().get('_auth_user_id')) == str(user.id):
            s.delete()

    send_mail('Kicked out {} from {}'.format(username, settings.MEDIAEVAL_MODALITY), 
              'For potential annotation cheating.', 
              'root@eye.hiit.fi', ['mats.sjoberg@helsinki.fi'], 
              fail_silently=False)

    return HttpResponseRedirect(reverse('annotate:cheat'))


#------------------------------------------------------------------------------

def get_unannotated():
    # Select a random pair to annotate
    # unannotated = ShotPair.objects.filter(status=ShotPair.UNANNOTATED)

    # Uncomment for ugly hack mode
    round=6
    # unannotated = ShotPair.objects.filter(status=ShotPair.UNANNOTATED,
    #                                      video__annotation_rounds=round)
    unannotated = ShotPair.objects.filter(status=ShotPair.UNANNOTATED, 
                                          video__annotation_rounds=round, 
                                          video__number__gte=0, 
                                          video__number__lte=103)
    count = len(unannotated)

    # Uncomment for normal mode
    # count=0
    
    if count==0:
        round=-1
        while count==0 and round<20:
            round += 1
            unannotated = ShotPair.objects.filter(status=ShotPair.UNANNOTATED,
                                                  video__annotation_rounds=round) #,
                                                  #video__number__gte=0, 
                                                  #video__number__lte=77)
            count = len(unannotated)

    return (unannotated, round)

#------------------------------------------------------------------------------

@login_required
def annotate(request):
    if 'start' not in request.POST:
        return HttpResponseRedirect(reverse('annotate:index'))

    annotator = get_annotator(request.user)

    if annotator is None:
        return HttpResponseRedirect(reverse('annotate:register_external'))

    if 'pair_id' in request.POST:
        # Annotated pair and sanity check that the shots are the same
        pair_id = int(request.POST['pair_id'])
        shot1_id = int(request.POST['shot1_id'])
        shot2_id = int(request.POST['shot2_id'])
        shot_pair = ShotPair.objects.get(id=pair_id)

        assert(shot1_id == shot_pair.shot_1.id)
        assert(shot2_id == shot_pair.shot_2.id)

        username = annotator.user.username

        if shot_pair.status in (ShotPair.UNANNOTATED, ShotPair.RESERVED):
            video = shot_pair.video
            s1 = shot_pair.shot_1
            s2 = shot_pair.shot_2

            if 'stop' in request.POST:
                # release this pair
                shot_pair.status = ShotPair.UNANNOTATED
                shot_pair.save()

                LOG.info('STOPPED: %s [video #%d] %d:%s %d:%s', username, 
                         video.number, 
                         s1.number, s1.filename, 
                         s2.number, s2.filename)
                return HttpResponseRedirect(reverse('annotate:index'))
            else:
                # Get selection
                if 'shot1' in request.POST and not 'shot2' in request.POST:
                    shot_pair.status = ShotPair.SHOT_1_SELECTED
                    annotator.annotation_count += 1
                elif 'shot2' in request.POST and not 'shot1' in request.POST:
                    shot_pair.status = ShotPair.SHOT_2_SELECTED
                    annotator.annotation_count += 1
                else:
                    LOG.error('Vote without selection!')
                    shot_pair.status = ShotPair.UNANNOTATED
                    raise Exception('Vote without selection!')

                cur_time = timezone.now()
                log_ann = LogAnnotation(annotator=annotator,
                                        video=video, shot_1=s1, shot_2=s2, 
                                        vote=shot_pair.status, 
                                        annotation_round=video.annotation_rounds,
                                        when=cur_time)

                shot_pair.save()
                annotator.save()
                log_ann.save()

                back_log_n = 40
                time_diff_check = 90
                LOG.info('VOTE: %s [video #%d] %d:%s %d:%s %d', username, 
                         video.number, 
                         s1.number, s1.filename, 
                         s2.number, s2.filename,
                         shot_pair.status)
                
                prev_logs = LogAnnotation.objects.filter(annotator=annotator).order_by('-when')[:back_log_n]

                if len(prev_logs) == back_log_n:
                    for l in prev_logs:
                        print(l)
                    lasti = back_log_n-1
                    tdiff = (cur_time-prev_logs[lasti].when).total_seconds()
                    if tdiff <= time_diff_check:
                        first_vote = prev_logs[lasti].vote
                        all_same = True
                        for i in range(lasti):
                            if prev_logs[i].vote != first_vote:
                                all_same = False
                                break

                        if all_same:
                            LOG.warn("Kicking out possible cheater: %s voted %d times the same in %d seconds.", username, back_log_n, tdiff)
                            return kick_out(annotator.user.username)
                    
        else:
            LOG.warn('Discarded old expired vote: %s, %d vs %d', username,
                     shot1_id, shot2_id)


    unannotated, round = get_unannotated()
    count = len(unannotated)

    # if there are none, go to the waiting page
    if count == 0:
        return render(request, 'annotate/wait.html',
                      {
                          'modality': settings.MEDIAEVAL_MODALITY,
                      })

    selected_index = random.randint(0, count-1)
    selected_pair = unannotated[selected_index]

    # ... and mark it as reserved
    selected_pair.status = ShotPair.RESERVED
    selected_pair.annotation_started = timezone.now()
    selected_pair.save()

    # Generate the annotation page
    shot1 = selected_pair.shot_1
    shot2 = selected_pair.shot_2

    basepath = 'videos/links/' + selected_pair.video.filename

    shot1video = basepath + '/movies/' + shot1.filename
    shot1image = basepath + '/images/midframe/' + shot1.image_filename

    shot2video = basepath + '/movies/' + shot2.filename
    shot2image = basepath + '/images/midframe/' + shot2.image_filename

    annotation_count = LogAnnotation.objects.filter(annotator=annotator, cheat=False).count()
    
    return render(request, 'annotate/annotate.html',
                  { 
                      'modality': settings.MEDIAEVAL_MODALITY,
                      'shot1' : shot1video,
                      'shot2' : shot2video,
                      'image1' : shot1image,
                      'image2' : shot2image,
                      'shot1_id': shot1.id,
                      'shot2_id': shot2.id,
                      'pair_id': selected_pair.id,
                      'annotation_count': annotation_count
                  })

#------------------------------------------------------------------------------

def is_organiser(user):
    return user.is_superuser or user.groups.filter(name='organiser').exists()

#------------------------------------------------------------------------------

# From here:
# http://codereview.stackexchange.com/questions/5196/grouping-consecutive-numbers-into-ranges-in-python-3-2

def as_range(iterable):
    l = list(iterable)
    if len(l) > 1:
        return '{0}-{1}'.format(l[0], l[-1])
    else:
        return '{0}'.format(l[0])
#------------------------------------------------------------------------------

@login_required
@user_passes_test(is_organiser)
def status(request):
    annotator = get_annotator(request.user)

    video_stats = {}

    target_round = 7
    tot_annot_left = 0
    
    for v in Video.objects.all():
        pairs_tot = ShotPair.objects.filter(video=v).count()
        pairs_unannotated = ShotPair.objects.filter(video=v, status=ShotPair.UNANNOTATED).count() + \
                            ShotPair.objects.filter(video=v, status=ShotPair.RESERVED).count()
        rounds_left = target_round-v.annotation_rounds
        annot_left = 0
        if rounds_left > 0:
            t = Shot.objects.filter(video=v).count()
            annot_per_round = int(t*(math.sqrt(t)-1))
            annot_left = (rounds_left-1)*annot_per_round + pairs_unannotated
        print(v.number, rounds_left, pairs_unannotated, annot_left)
        tot_annot_left += annot_left
        video_stats[v.number] = {
            'status': ('annotating', 'calculating BTL')[v.status],
            'doing_round': v.annotation_rounds+1,
            'pairs_done': 100.0 * (pairs_tot-pairs_unannotated) / pairs_tot,
            'pairs_unannotated': pairs_unannotated,
            'annot_left': annot_left
        }

    unannotated, round = get_unannotated()

    vnums = sorted(unannotated.values_list('video__number', flat=True).distinct())

    rangestr = ', '.join(as_range(g) for _, g in groupby(vnums, key=lambda n, c=count(): n-next(c)))

    queue_round = round+1
    if len(unannotated) == 0:
        queue_round = "-"

    return render(request, 'annotate/status.html',
                  {
                      'modality': settings.MEDIAEVAL_MODALITY,
                      'total_annotations': LogAnnotation.objects.filter(cheat=False).count(),
                      'video_stats': video_stats,
                      'last_annotations': LogAnnotation.objects.order_by('-when'),
                      'queue_round': queue_round,
                      'queue_videos': rangestr,
                      'queue_size': len(unannotated),
                      'tot_annot_left': tot_annot_left,
                      'target_round': target_round+1
                  })

#------------------------------------------------------------------------------

@login_required
@user_passes_test(is_organiser)
def log(request):
    return render(request, 'annotate/log.html',
                  {
                      'modality': settings.MEDIAEVAL_MODALITY,
                      'total_annotations': LogAnnotation.objects.filter(cheat=False).count(),
                      'last_annotations': LogAnnotation.objects.order_by('-when')
                  })

#------------------------------------------------------------------------------

@login_required
@user_passes_test(is_organiser)
def annotators(request):
    if 'since' in request.GET:
        since = request.GET['since']
        ct = Count(Case(When(Q(logannotation__when__gt=since) & Q(logannotation__cheat=False), then=1), output_field=IntegerField()))
        #ct = Count(Case(When(logannotation__when__gt=since, then=1), output_field=IntegerField()))
    else:
        since = '2017-02-07'
        ct = Count(Case(When(logannotation__cheat=False, then=1), output_field=IntegerField()))
        #ct = Count('logannotation')
        
    anns = Annotator.objects.annotate(num_logged=ct).filter(num_logged__gt=0).order_by('-num_logged')

    return render(request, 'annotate/status_annotators.html',
                  {
                      'modality': settings.MEDIAEVAL_MODALITY,
                      'since': since,
                      'annotators': anns
                  })
