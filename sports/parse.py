import sys
sys.path.append('/users/u20/tcohen/.virtualenvs/tcohen/lib/python2.7/site-packages')

import mechanize
import re
from bs4 import BeautifulSoup
from models import Team, Player, Matchup, Authenticate, Season

def mechrequest():
        url = 'https://imleagues.com/Login.aspx'
        br = mechanize.Browser()
        br.set_handle_robots(False) 
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        br.open(url)
        response = br.response().read()
        br.select_form(nr=0) 
        br.set_all_readonly(False)
        mnext = re.search("""<a id="ctl00_ContentPlaceHolder1_btnLogin" tabindex="4" class="login" href="javascript:__doPostBack\('(.*?)','(.*?)'\)" style""", response)
        user = Authenticate.objects.all()[0]
        br.form["ctl00$ContentPlaceHolder1$inUserName"] = user.imusername
        br.form["ctl00$ContentPlaceHolder1$inPassword"] = user.impassword
        br["__EVENTTARGET"] = mnext.group(1)
        br["__EVENTARGUMENT"] = mnext.group(2)
        br.submit()
        return br #Returns the browser that has logged in

def getName(soup):
    div = soup.find(id="ctl00_ContentPlaceHolder2_upgamestatus") #sets div to the div where the name is locatd
    return div.find_all("td")[2].get_text().strip().split(",")[0] #returns the name from the div

def getPicture(string):
    """
    takes in the link to the picture and returns the bigger size if available
    """
    x = list(string)
    x[-5] = "m"
    y = "".join(x)
    return y

def getMatchups(soup, _cshTeam, url):
    x = soup.find_all(text=re.compile(_cshTeam))
    _csh_wins = 0
    _csh_losses = 0
    _csh_ties = 0
    sportContent = soup.find_all("div", { "class" : "popover-content" })[0]
    li = sportContent.find_all("li")[2]
    _sport = li.find_next("a").get_text()
    header = soup.find(id="ctl00_ucSiteHeader_divHeaderBox")
    csh_picture = header.find_next("img").get("src")
    try:
        cshTeam = Team.objects.get(link=url)
    except:
        cshTeam = None
    if cshTeam:
        cshTeam.picture = csh_picture
        cshTeam.save()
    else:
        cshTeam = Team(link=url, sport=_sport, name=_cshTeam, wins=_csh_wins, losses=_csh_losses, ties=_csh_ties, picture=csh_picture, rank=0, iscsh=True, season=Season.objects.all()[0].season)
        cshTeam.save()
    overall = soup.find(id="ctl00_ContentPlaceHolder2_ucTeamRelated_pnlTeamSchedule")
    teamSchedule = overall.find_next("tbody")
    if (teamSchedule == None):
        print("No team schedule found.")
    else:
        counter = 0
        teams = teamSchedule.find_all("tr")
        year = overall.get_text()[1:5]
        endofyear = False
        for i in range(len(teams)//2):
            match = teams[counter].find_all("td")
            _date = match[0].get_text() + " " + year
            if _date.split(" ")[1] == "Dec":
                endofyear = True
            if endofyear == True and _date.split(" ")[1] != "Dec":
                newyear = str(int(_date.split(" ")[3])+1)
                _date = match[0].get_text() + " " + newyear
            opponent = match[1].get_text().split("  ")
            _enemyTeam = opponent[1]
            loc = opponent[0] #gets whether it is VS or @
            result = match[2].get_text().split()
            _outcome = result[0] #gets whether it was a W or L or T
            if (_outcome != "W") and (_outcome != "L") and (_outcome != "T"): #if matchup hasn't happened yet
                _outcome = None
                _upcoming = match[2].get_text()
            else:
                if (loc == "VS"):
                    _cshScore = result[1]
                    _enemyScore = result[3]
                else:
                    _cshScore = result[3]
                    _enemyScore = result[1]
            record = match[4].get_text().split("-")
            _wins = record[0]
            _losses = record[1]
            _ties = record[2]
            enemyUrl = match[1].find_next("a").get("href")
            pictureLink = match[1].find_next("img").get("src")
            if ("DefaultLogo" in pictureLink):
                _picture = pictureLink
            else:
                _picture = getPicture(pictureLink)
            if (_outcome == "W"):
                _csh_wins += 1
            elif (_outcome == "L"):
                _csh_losses += 1
            elif (_outcome == "T"):
                _csh_ties += 1
            counter += 2
            try:
                enemyTeam = Team.objects.get(link=enemyUrl)
            except:
                enemyTeam = None
            if enemyTeam:
                enemyTeam.wins = _wins
                enemyTeam.losses = _losses
                enemyTeam.ties = _ties
                enemyTeam.picture =_picture
                enemyTeam.rank = getRank(soup, enemyTeam.name, _wins, _losses, _ties) 
                enemyTeam.save()
            else:
                enemyTeam = Team(link=enemyUrl, sport=_sport, name=_enemyTeam, wins=_wins, losses=_losses, ties=_ties, picture=_picture, rank=getRank(soup, _enemyTeam, _wins, _losses, _ties), iscsh=False, season=Season.objects.all()[0].season)
                enemyTeam.save()
            oldmatch = cshTeam.CSH.filter(enemy = enemyTeam)
            happened = None
            if len(oldmatch) != 0:
                for game in oldmatch:
                    if game.date == _date:
                        happened = game
            if happened: #if matchup made
                if _outcome: #if game happened
                    happened.cshScore = _cshScore
                    happened.enemyScore = _enemyScore
                    happened.outcome = _outcome
                    happened.save()
                else:
                    happened.upcoming = _upcoming
                    happened.date = _date
                    happened.save()
            else:
                if _outcome:
                    matchup = Matchup(csh=cshTeam, enemy=enemyTeam, cshScore=_cshScore, enemyScore=_enemyScore, outcome=_outcome, date=_date)
                    matchup.save()
                else:
                    matchup = Matchup(csh=cshTeam, enemy=enemyTeam,cshScore=None, enemyScore=None, upcoming=_upcoming, date=_date)
                    matchup.save()


    cshTeam.wins = _csh_wins
    cshTeam.losses = _csh_losses
    cshTeam.ties = _csh_ties
    cshTeam.rank = getRank(soup, cshTeam.name, _csh_wins, _csh_losses, _csh_ties)
    cshTeam.save()
        
def getRank(soup, name, wins, losses, ties):
    standings = soup.find("div", { "class" : "right_box_content" }).find_all("tr")[1:]
    rank = 1
    for standingteam in standings:
        standingname = standingteam.find_all("td")[0].get_text().strip()
        standingscore = standingteam.find_all("td")[1].get_text()
        if standingname == name and standingscore == str(wins) + "-" + str(losses) + "-" + str(ties):
            return rank
        rank += 1
    return None
 


def getRoster(soup, url):
    mydivs = soup.find_all("div", { "class" : "popover-content" })[1] #Sets mydivs to the div containing the roster
    link = mydivs.find_next("a").get("href")
    rosterLink = "https://www.imleagues.com/School/Team/" + link
    br = mechrequest()
    br.open(rosterLink)
    html = br.response().read()
    soup = BeautifulSoup(html)
    _team = Team.objects.get(link=url)
    overall = soup.find(id="ctl00_ContentPlaceHolder1_gvTeamMembers")
    roster = overall.find_all("tr")
    players = roster[2:(len(roster)-1)]
    counter = 0
    for i in range(len(players)//2):
        _player = players[counter]
        _picture = _player.find_next("img").get("src")
        _link = _player.find_next("a").get("href")
        bio = _player.find_all("td")[2]
        _name = bio.find_all("div")[0].get_text().title()
        _gender = bio.find_all("div")[1].get_text().split(" ")[1]
        status = _player.find_all("td")[3]
        capt = status.find_all("div")[0].get_text()
        if capt != "Member":
            _iscaptain = True
        else:
            _iscaptain = False
        try:
            oldPlayer = Player.objects.get(link=_link)
        except:
            oldPlayer = None
        if oldPlayer:
            oldPlayer.picture = _picture
            oldPlayer.team.add(_team)
            oldPlayer.save()
        else:
            player = Player(link=_link, name=_name, gender=_gender, picture=_picture, iscaptain=_iscaptain)
            player.save()
            player.team.add(_team)
            player.save()
        counter += 2

def getTeamsOn(link):
    br = mechrequest()
    br.open(link)
    html = br.response().read()
    soup = BeautifulSoup(html)

def getData(url):
    br = mechrequest()
    br.open(url) #Opens the url in the browser
    html = br.response().read() #Sets HTML to the read in source code
    soup = BeautifulSoup(html) #Sets soup to use beautifulsoup with html
    _cshTeam = getName(soup) #Sets cshTeam to the name of the CSH team returned in getName
    print("Currently updating for CSH team:", _cshTeam)
    getMatchups(soup, _cshTeam, url)
    getRoster(soup, url)

def update():
    urlList = [team.link for team in Team.objects.filter(iscsh=True).filter(season=Season.objects.get(pk=1).season)]
    for url in urlList:
        getData(url)
    #broomball = "http://www.imleagues.com/School/Team/Home.aspx?Team=57a774ebc1e24dafa4c98c1fea9fcbd0"
    #soccer = "http://www.imleagues.com/School/Team/Home.aspx?Team=2ea5850d537a423eb5a086a72d0ac16a"
    #volleyball = "http://www.imleagues.com/School/Team/Home.aspx?Team=1e89a62bdcda460d97acb64179093572"
