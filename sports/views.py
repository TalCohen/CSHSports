from sports.models import Team, Player, Matchup, Authenticate, Season
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
import time
from datetime import date
import sha
import parse

def playerdetails(request, user_id):
    p = get_object_or_404(Player, pk=user_id)
    isEmpty = False
    teamList = p.team.filter(season=Season.objects.get(pk=1).season)
    if teamList == 0:
        isEmpty = True
    length = len(teamList)
    for team in teamList:
        if length >= 3:
            team.name = fixedSizeTeam(team.name)
        matchupList = team.CSH.all()
        team.nextGame = getUpcoming(matchupList)
    teams = Team.objects.filter(iscsh=True).filter(season=Season.objects.get(pk=1).season)
    return render_to_response('CSHSports/player.html', {'player': p, 'teams': teamList, 'length': length, 'teamList': teams, 'isEmpty': isEmpty}, context_instance=RequestContext(request))

def allplayers(request):
    latest = Player.objects.all() 
    return render_to_response('example/index.html', {'latest_player_list': latest}, context_instance=RequestContext(request))

def allteams(request):
    teams = Team.objects.filter(iscsh=True).filter(season=Season.objects.get(pk=1).season)
    for team in teams:
        team.name = fixedSizeTeam(team.name)
    return render_to_response('CSHSports/index.html', {'teamList': teams}, context_instance=RequestContext(request))

def teamdetails(request, team_id):
    t = get_object_or_404(Team, pk=team_id)
    matchupList = t.CSH.all() 
    playerList = t.player_set.all()
    playerList = list(playerList)
    for player in playerList:
        player.name = fixedSizePlayer(player.name)
        if player.iscaptain:
            playerList.insert(0, playerList.pop(playerList.index(player)))
    side1 = playerList[::2]
    side2 = playerList[1::2]
    teams = Team.objects.filter(iscsh=True).filter(season=Season.objects.get(pk=1).season)
    infoDict = {'team': t, 'side1': side1, 'side2': side2, 'matchup':getUpcoming(matchupList), 'teamList': teams}
    return render_to_response('CSHSports/teamdetails.html', infoDict, context_instance=RequestContext(request))

def matchups(request, team_id):
    t = get_object_or_404(Team, pk=team_id)
    matchupList = t.CSH.all()
    teams = Team.objects.filter(iscsh=True).filter(season=Season.objects.get(pk=1).season)
    infoDict = {'team': t, 'matchups': matchupList, 'matchupnext':getUpcoming(matchupList), 'year': matchupList[0].date.split(" ")[3], 'teamList': teams}
    return render_to_response('CSHSports/matchups.html', infoDict, context_instance=RequestContext(request))


def getUpcoming(matchupList):
    timeSet = [(time.strptime(match.date,"%a, %b %d %Y"), match) for match in matchupList]
    timeToday = time.strptime(str(date.today().day) + " " + str(date.today().month) + " " + str(date.today().year), "%d %m %Y")
    for dates in timeSet:
        if dates[0] >= timeToday:
            return dates[1]
    return None

def auth(request):
    if 'login' in request.session and request.session['login']:
        return True
    if not request.POST:
        return False
    authList = Authenticate.objects.all()
    for a in authList:
        if(a.username == request.POST['user']) and (a.password == sha.new(request.POST['pwd']).hexdigest()):
            request.session['login'] = True
            request.session['invalid'] = False
            return True
    request.session['invalid'] = True
    return False
          
def login(request):
    if auth(request):
        return redirect('/admin/')
    else:
        if 'invalid' in request.session and request.session['invalid']:
            invalid = True
        else:
            invalid = False
        return render_to_response('CSHSports/login.html', {'invalid': invalid}, context_instance=RequestContext(request))

def admin(request):
    if auth(request):
        teamList = Team.objects.filter(iscsh=True).filter(season=Season.objects.get(pk=1).season)
        s = Season.objects.get(pk=1).season
        return render_to_response('CSHSports/admin.html', {'teams' : teamList, 'season' : s}, context_instance=RequestContext(request))
    else:
        return redirect('/login/')

def addteams(request):
    if auth(request):
        return render_to_response('CSHSports/addteams.html', context_instance=RequestContext(request))
    else:
        return redirect('/login/')

def maketeams(request):
    if auth(request):
        parse.getData(request.POST['url']) # Sanitize your inputs
        t = Team.objects.get(link=request.POST['url'])
        #return redirect('/team/' + str(t.id) + '/')
        return redirect('/admin/')
    else:
        return redirect('/login/')

#fix changeseason to be behind auth. have a logout button. maybe fix up /make.



def changeseason(request):
    if auth(request):
        s = Season.objects.get(pk=1).season
        return render_to_response('CSHSports/changeseason.html', {'season' : s}, context_instance=RequestContext(request))
    else:
        return redirect('/login/')

def change(request):
    if auth(request):
        s = Season.objects.get(pk=1)
        if 'choice' in request.POST and request.POST['choice'] == 'forward': 
            s.season += 1
            s.save()
        elif 'choice' in request.POST and request.POST['choice'] == 'back' and s.season != 1:
            s.season -= 1
            s.save()
        return redirect('/admin/')
    else:
        return redirect('/login/')

def logout(request):
    if auth(request):
        request.session['login'] = False
    return redirect('/login')

def fixedSizePlayer(name):
    if len(name) > 18:
        name = name[:18] + "..."
    return name

def fixedSizeTeam(name):
    if len(name) > 14:
        name = name[:14] + "..."
    return name
