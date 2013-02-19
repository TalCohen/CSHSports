import mechanize
import re
from bs4 import BeautifulSoup
from models import Team, Player, Matchup

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
        br.form["ctl00$ContentPlaceHolder1$inUserName"] = "tsc1510@rit.edu"
        br.form["ctl00$ContentPlaceHolder1$inPassword"] = "cshsportsaregreat"
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
    print(_cshTeam)
    x = soup.find_all(text=re.compile(_cshTeam))
    print(len(x))
    _csh_wins = 0
    _csh_losses = 0
    _csh_ties = 0
    """if (len(x) > 3):
        y = x[len(x)-1].parent
        z = y.get_text().split()
        print("Z", z)
        #csh_record = z[1].split("(")[1].split(")")[0].split("-") #gets the csh record #re.findall("\d+", "(42-2-0)") and import re
        csh_record = re.findall("\d+", z[1])
        _csh_wins = int(csh_record[0])
        _csh_losses = int(csh_record[1])
        _csh_ties = int(csh_record[2])"""
    sportContent = soup.find_all("div", { "class" : "popover-content" })[0]
    li = sportContent.find_all("li")[2]
    _sport = li.find_next("a").get_text()
    print(_sport)
    header = soup.find(id="ctl00_ucSiteHeader_divHeaderBox")
    csh_picture = header.find_next("img").get("src")
    print(csh_picture)
    print("csh score:", _csh_wins, _csh_losses, _csh_ties)
    #standings = soup.find("div", { "class" : "right_box_content" }).find_all("tr")[1:]
    #for standingteam in standings:
        #index = 1
        #standingname = standingteam.find_all("td")[0].get_text().strip()
        #standingscore = standingteam.find_all("td")[1].get_text()
        #print(standingname, standingscore)
        #if standingname == _enemyTeam and standingscore == _wins + "-" + _losses + "-" + _ties:
            #_rank = index
        #index += 1
    try:
        cshTeam = Team.objects.get(link=url)
    except:
        cshTeam = None
    if cshTeam:
        """cshTeam.wins = _csh_wins
        cshTeam.losses = _csh_losses
        cshTeam.ties = _csh_ties"""
        cshTeam.picture = csh_picture
        cshTeam.save()
    else:
        cshTeam = Team(link=url, sport=_sport, name=_cshTeam, wins=_csh_wins, losses=_csh_losses, ties=_csh_ties, picture=csh_picture, rank=0, iscsh=True)
        cshTeam.save()
    overall = soup.find(id="ctl00_ContentPlaceHolder2_ucTeamRelated_pnlTeamSchedule")
    teamSchedule = overall.find_next("tbody")
    #print(teamSchedule)
    if (teamSchedule == None):
        print("No team schedule found.")
    else:
        counter = 0
        teams = teamSchedule.find_all("tr")
        year = overall.get_text()[1:5]
        print(year)
        endofyear = False
        for i in range(len(teams)//2):
            match = teams[counter].find_all("td")
            _date = match[0].get_text() + " " + year
            if _date.split(" ")[1] == "Dec":
                endofyear = True
            if endofyear == True and _date.split(" ")[1] != "Dec":
                print("next year not december")
                print(int(_date.split(" ")[3])+1)
                newyear = str(int(_date.split(" ")[3])+1)
                _date = match[0].get_text() + " " + newyear
            print(_date)
            print(endofyear)
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
            #for standingteam in standings:
                #index = 1
                #standingname = standingteam.find_all("td")[0].get_text().strip()
                #standingscore = standingteam.find_all("td")[1].get_text()
                #print(standingname, standingscore)
                #if standingname == _enemyTeam and standingscore == _wins + "-" + _losses + "-" + _ties:
                    #_rank = index
                #index += 1
            enemyUrl = match[1].find_next("a").get("href")
            print(enemyUrl)
            pictureLink = match[1].find_next("img").get("src")
            if ("DefaultLogo" in pictureLink):
                _picture = pictureLink
            else:
                _picture = getPicture(pictureLink)
            print(_picture)
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
                print("i error here")
                enemyTeam = Team(link=enemyUrl, sport=_sport, name=_enemyTeam, wins=_wins, losses=_losses, ties=_ties, picture=_picture, rank=getRank(soup, _enemyTeam, _wins, _losses, _ties), iscsh=False)
                enemyTeam.save()
            try:
                happened = cshTeam.CSH.get(enemy = enemyTeam)
            except:
                happened = None
            if happened: #if matchup made
                if _outcome: #if game happened
                    happened.cshScore = _cshScore
                    happened.enemyScore = _enemyScore
                    happened.outcome = _outcome
                    happened.save()
                    #matchup = Matchup(csh=cshTeam, enemy=enemyTeam, cshScore=_cshScore, enemyScore=_enemyScore, outcome=_outcome, date=_date)
                    #matchup.save()
                else:
                    happened.upcoming = _upcoming 
                    happened.save()
            else:
                if _outcome:
                    matchup = Matchup(csh=cshTeam, enemy=enemyTeam, cshScore=_cshScore, enemyScore=_enemyScore, outcome=_outcome, date=_date)
                    matchup.save()
                else:
                    matchup = Matchup(csh=cshTeam, enemy=enemyTeam,cshScore=None, enemyScore=None, upcoming=_upcoming, date=_date)
                    matchup.save()


            print(_csh_wins, _csh_losses, _csh_ties)
    #if (len(x) <= 3):
    cshTeam.wins = _csh_wins
    cshTeam.losses = _csh_losses
    cshTeam.ties = _csh_ties
    cshTeam.rank = getRank(soup, cshTeam.name, _csh_wins, _csh_losses, _csh_ties)
    cshTeam.save()
        
#def getRosterLink(soup):
#    """
#    getName takes in a snippet of html and returns the CSH team name
#    """
#    mydivs = soup.find_all("div", { "class" : "popover-content" })[1] #Sets mydivs to the div containing the roster
#    link = mydivs.find_next("a").get("href")
#    rosterLink = "https://www.imleagues.com/School/Team/" + link
#    print(rosterLink)
#    return rosterLink

def getRank(soup, name, wins, losses, ties):
    standings = soup.find("div", { "class" : "right_box_content" }).find_all("tr")[1:]
    rank = 1
    for standingteam in standings:
        standingname = standingteam.find_all("td")[0].get_text().strip()
        standingscore = standingteam.find_all("td")[1].get_text()
        print(standingname, standingscore, "checking the team", name, wins, losses, ties)
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
        print(_picture, _link, _name, _gender, _iscaptain)
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

   # if roster[0].find(id="ctl00_ContentPlaceHolder1_gvTeamMembers_ctl01_GridPager1_GridPager"):
   ##     nav = roster[0].find(id="ctl00_ContentPlaceHolder1_gvTeamMembers_ctl01_GridPager1_GridPager")
   #     buttons = nav.find_all("li")
   #     nxt = buttons[len(buttons)-1]
   #     print(nxt)
   #     br = mechrequest()
   #     response = br.open(link)
   #     for i in range(10):
   #         html = response.read()
   #         #print("Page %d :" % i, html)
   #         br.select_form(nr=0)
   #         #print(br.form)
   #         br.set_all_readonly(False)
   #         #mnext = re.search("""<a href="#" onclick="javascript:__doPostBack\('(.*?)','(.*?)'\);" style="color:#ffffff;">Next""", html)
   #         #if not mnext:
   #         #    print("not mnext")
   #         #    break
   #         #print("this is mnext")
   #         br["__EVENTTARGET"] = 'ctl00$ContentPlaceHolder1$gvTeamMembers' #mnext.group(1)
   #         br["__EVENTARGUMENT"] = 'page$2' #mnext.group(2)
   #         #br.find_control("btnSearch").disabled = True
   #         response = br.submit()
   ##         newhtml = response.read()
   #         newsoup = BeautifulSoup(newhtml)
   #         newoverall = soup.find(id="ct100_contentPlaceHolder1_gvTeamMembers")
   #         newroster = overall.find_all("tr")
   #         newplayers = newroster[2:(len(newroster)-1)]
   #         newbio = players[0].find_all("td")[2].find_all("div")[0].get_text()
   #         print(newbio)



   # else:
   #     print("THIS DOESNT HAVE IT!")
   # return


def getTeamsOn(link):
    br = mechrequest()
    br.open(link)
    html = br.response().read()
    soup = BeautifulSoup(html)



"""def getSport(soup):
    mydivs = soup.find_all("div", { "class" : "popover-content" })[0]
    li = mydivs.find_all("li")[2]
    sport = li.find_next("a").get_text()
"""    


def main():
    br = mechrequest() #Sets br to the browser that logs in
    broomball = "http://www.imleagues.com/School/Team/Home.aspx?Team=57a774ebc1e24dafa4c98c1fea9fcbd0"
    soccer = "http://www.imleagues.com/School/Team/Home.aspx?Team=2ea5850d537a423eb5a086a72d0ac16a"
    volleyball = "http://www.imleagues.com/School/Team/Home.aspx?Team=1e89a62bdcda460d97acb64179093572"
    cshTeamList=[broomball, soccer, volleyball]
    for team in cshTeamList:
        br.open(team) #Opens the url in the browser
        html = br.response().read() #Sets HTML to the read in source code
        soup = BeautifulSoup(html) #Sets soup to use beautifulsoup with html
        _cshTeam = getName(soup) #Sets cshTeam to the name of the CSH team returned in getName
        getMatchups(soup, _cshTeam, team)
        #rosterLink = getRosterLink(soup)
        getRoster(soup, team)



#if dont have team, make a new team. otherwise proceed to matchup table. make foreign key
#match to whatever team they are. Hold on to it. Have it on hand.
