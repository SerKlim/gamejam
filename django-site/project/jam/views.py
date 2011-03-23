from models import *
from datetime import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from forms import RatingForm
from django.db.models import Avg, Count
from django.template import RequestContext

def get_next_entry(request, jam):
    try:
        return Entry.objects.filter(gamejam=jam).exclude(user__pk=request.user.pk).exclude(vote__user__pk=request.user.pk).annotate(votes=Count('vote')).order_by('votes')[0]
    except IndexError:
        return None

def jam_detail(request, jam_id):
    jam = get_object_or_404(Jam, pk=jam_id)
    user_profile = None
    if request.user.is_authenticated():
        user_profile = request.user.get_profile()
    now = datetime.now()

    not_started = now < jam.date_start
    not_finished = jam.date_start < now < jam.date_end
    voting_period = jam.date_end < now < jam.date_vote_end
    can_vote = user_profile and user_profile.can_vote
    cant_vote = not can_vote and voting_period
    voting = can_vote and voting_period
    entries = None
    if now > jam.date_vote_end:
        entries = Entry.objects.all()
    next_entry = None
    if voting:
        next_entry = get_next_entry(request, jam)
    
    return render_to_response('jam/jam_detail.html', {
        'jam': jam,
        'not_started': not_started,
        'not_finished': not_finished,
        'cant_vote': cant_vote,
        'entries': entries,
        'voting': voting,
        'next_entry': next_entry,
    }, context_instance=RequestContext(request))

def entry_detail(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    user_profile = None
    if request.user.is_authenticated():
        user_profile = request.user.get_profile()
    now = datetime.now()
    voting = user_profile and user_profile.can_vote and request.user != entry.user and entry.gamejam.date_end < now < entry.gamejam.date_vote_end and Vote.objects.filter(user=request.user, entry=entry).count() == 0
    if not voting and now < entry.gamejam.date_vote_end:
        raise Http404
    rating_form = None
    next_entry = None
    if voting:
        if request.method == 'POST':
            abstain = 'abstain' in request.POST
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid() or abstain:
                vote = Vote()
                vote.user = request.user
                vote.entry = entry
                vote.abstain = abstain
                vote.save()
                if not abstain:
                    rating = rating_form.save(commit=False)
                    rating.vote = vote
                    rating.save()
                next_entry = get_next_entry(request, entry.gamejam)
                if next_entry:
                    return HttpResponseRedirect(next_entry.get_absolute_url())
                else:
                    return HttpResponseRedirect('/jams/voting-finished/')
        else:
            rating_form = RatingForm()
    rating = {}
    if now > entry.gamejam.date_vote_end:
        rating['gameplay'] = entry.vote_set.aggregate(Avg('rating__gameplay')).values()[0]
        rating['graphics'] = entry.vote_set.aggregate(Avg('rating__graphics')).values()[0]
        rating['music'] = entry.vote_set.aggregate(Avg('rating__music')).values()[0]
        rating['fun'] = entry.vote_set.aggregate(Avg('rating__fun')).values()[0]
        rating['overall'] = entry.vote_set.aggregate(Avg('rating__overall')).values()[0]

    return render_to_response('jam/entry_detail.html', {
        'entry': entry,
        'rating_form': rating_form,
        'rating': rating,
    }, context_instance=RequestContext(request))
