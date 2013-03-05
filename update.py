#!/usr/bin/env python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sports.settings")

#from sports.models import Team, Player, Matchup, Authenticate

#literally any python/django code here

import sports.parse
sports.parse.update()
