from sports.models import Team, Player, Matchup, Authenticate, Season
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils import timezone
import time
from datetime import date, datetime, timedelta
import sha
import parse

def home(request):
    """
    Gets the name of the person signing in from ldap to make their homepage
    their personal player page
    """
    #request.META["HTTP_X_WEBAUTH_LDAP_CN"] = Common Name
    #request.META["HTTP_X_WEBAUTH_USER"] = CSH Name
    pList = Player.objects.all()
    name = request.META["HTTP_X_WEBAUTH_LDAP_CN"]
    newName = name.split(" ")
    if len(newName) > 2:
        newName = newName[0] + " " + newName[len(newName)-1]
        name = newName
    for player in pList:
        tList = player.team.filter(season=Season.objects.get(pk=1).season)
        if player.name == name and len(tList) > 0:
            return playerdetails(request, player.id)
    return redirect('/allteams/')

def playerdetails(request, user_id):
    """
    Gets the information to populate each player page, with the teams they are
    playing on
    """
    p = get_object_or_404(Player, pk=user_id)
    isEmpty = False
    teamList = p.team.filter(season=Season.objects.get(pk=1).season)
    if len(teamList) == 0:
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
    """
    Gets every player in the database
    """
    latest = Player.objects.all() 
    return render_to_response('example/index.html', {'latest_player_list': latest}, context_instance=RequestContext(request))

def allteams(request):
    """
    Gets the information to populate the main page with all the teams
    """
    teams = Team.objects.filter(iscsh=True).filter(season=Season.objects.get(pk=1).season)
    for team in teams:
        team.name = fixedSizeTeam(team.name)
    return render_to_response('CSHSports/allteams.html', {'teamList': teams}, context_instance=RequestContext(request))

def teamdetails(request, team_id):
    """
    Gets the information to populate the team page with the next upcoming game,
    and roster
    """
    t = get_object_or_404(Team, pk=team_id)
    unsortedMatchupList = list(t.CSH.all())
    matchupList = sorted(unsortedMatchupList, key=lambda m: m.date)
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
    """
    Gets the information to populate each team's schedule
    """
    t = get_object_or_404(Team, pk=team_id)
    unsortedMatchupList = list(t.CSH.all())
    matchupList = sorted(unsortedMatchupList, key=lambda m: m.date)
    teams = Team.objects.filter(iscsh=True).filter(season=Season.objects.get(pk=1).season)
    infoDict = {'team': t, 'matchups': matchupList, 'matchupnext':getUpcoming(matchupList), 'year': matchupList[0].clean_date.split(" ")[3], 'teamList': teams}
    return render_to_response('CSHSports/matchups.html', infoDict, context_instance=RequestContext(request))

def getUpcoming(matchupList):
    """
    Gets the next upcoming game, given a list of matchups
    """
    timeSet = [(match.date, match) for match in matchupList]
    timeToday = (timezone.make_aware(datetime.now(), timezone.get_default_timezone())) - timedelta(days=1)
    for dates in timeSet:
        if dates[0] >= timeToday and len(dates[1].outcome) == 0:
            return dates[1]
    return None

def auth(request):
    """
    The main function for the auth required to access the admin hub
    """
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
    """
    Gets the information for the login page
    """
    if auth(request):
        return redirect('/admin/')
    else:
        if 'invalid' in request.session and request.session['invalid']:
            invalid = True
        else:
            invalid = False
        return render_to_response('CSHSports/login.html', {'invalid': invalid}, context_instance=RequestContext(request))

def admin(request):
    """
    Gets the information for the admin hub main page
    """
    if auth(request):
        teamList = Team.objects.filter(iscsh=True).filter(season=Season.objects.get(pk=1).season)
        s = Season.objects.get(pk=1).season
        return render_to_response('CSHSports/admin.html', {'teams' : teamList, 'season' : s}, context_instance=RequestContext(request))
    else:
        return redirect('/login/')

def addteams(request):
    """
    Gets the information for the addteams page in the admin hub
    """
    if auth(request):
        return render_to_response('CSHSports/addteams.html', context_instance=RequestContext(request))
    else:
        return redirect('/login/')

def maketeams(request):
    """
    Actually adds the team that was requested by the addteams page
    """
    #fh = open("log.txt")
    #fh.write("I got to step 1 \n")
    if auth(request):
        parse.getData(request.POST['url']) # Sanitize your inputs
        #fh.write("I got to step 2 \n")
        t = Team.objects.get(link=request.POST['url'])
        #fh.write("I got to step 3 \n")
        return redirect('/admin/')
    else:
        return redirect('/login/')

def changeseason(request):
    """
    Gets the information for the changeseason page in the admin hub
    """
    if auth(request):
        s = Season.objects.get(pk=1).season
        return render_to_response('CSHSports/changeseason.html', {'season' : s}, context_instance=RequestContext(request))
    else:
        return redirect('/login/')

def change(request):
    """
    Actually changes the season that was requested from the admin hub
    """
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
    """
    Logs the user out from the admin hub
    """
    if auth(request):
        request.session['login'] = False
    return redirect('/login')

def fixedSizePlayer(name):
    """
    Takes a player name and changes the player name to fit the template
    """
    if len(name) > 18:
        name = name[:18] + "..."
    return name

def fixedSizeTeam(name):
    """
    Takes a team name and changes the team name to fit the template
    """
    if len(name) > 14:
        name = name[:14] + "..."
    return name
