from sports.models import Team, Player, Matchup, Authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
import time
from datetime import date
import sha

#returns a webpage with all of the information about player based on the userid
def playerdetails(request, user_id):
    p = get_object_or_404(Player, pk=user_id)
    teamList = p.team.all()
    length = len(teamList)
    for team in teamList:
        if length >= 3:
            team.name = fixedSizeTeam(team.name)
        matchupList = team.CSH.all()
        team.nextGame = getUpcoming(matchupList)
    teams = Team.objects.filter(iscsh=True)
    return render_to_response('CSHSports/player.html', {'player': p, 'teams': teamList, 'length': length, 'teamList': teams}, context_instance=RequestContext(request))

def allplayers(request):
    latest = Player.objects.all() 
    return render_to_response('example/index.html', {'latest_player_list': latest}, context_instance=RequestContext(request))



def allteams(request):
    teams = Team.objects.filter(iscsh=True)
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
    teams = Team.objects.filter(iscsh=True)
    infoDict = {'team': t, 'side1': side1, 'side2': side2, 'matchup':getUpcoming(matchupList), 'teamList': teams}
    return render_to_response('CSHSports/teamdetails.html', infoDict, context_instance=RequestContext(request))

def matchups(request, team_id):
    t = get_object_or_404(Team, pk=team_id)
    matchupList = t.CSH.all()
    teams = Team.objects.filter(iscsh=True)
    infoDict = {'team': t, 'matchups': matchupList, 'matchupnext':getUpcoming(matchupList), 'year': matchupList[0].date.split(" ")[3], 'teamList': teams}
    return render_to_response('CSHSports/matchups.html', infoDict, context_instance=RequestContext(request))


def getUpcoming(matchupList):
    timeSet = [(time.strptime(match.date,"%a, %b %d %Y"), match) for match in matchupList]
    timeToday = time.strptime(str(date.today().day) + " " + str(date.today().month) + " " + str(date.today().year), "%d %m %Y")
    for dates in timeSet:
        if dates[0] >= timeToday:
            return dates[1]
    return None


def addteams(request):
    return render_to_response('CSHSports/addteams.html', context_instance=RequestContext(request))

def maketeams(request):
    a = Authenticate.objects.get(pk=1)
    if(a.password == sha.new(request.POST['pwd']).hexdigest()):
        return
    else:
        return HttpResponse("You did not")


def fixedSizePlayer(name):
    if len(name) > 18:
        name = name[:18] + "..."
    return name

def fixedSizeTeam(name):
    if len(name) > 14:
        name = name[:14] + "..."
    return name
