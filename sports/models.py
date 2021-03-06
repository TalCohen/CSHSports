# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Team(models.Model):
    link = models.CharField(max_length=200)
    sport = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    wins = models.IntegerField()
    losses = models.IntegerField()
    ties = models.IntegerField()
    picture = models.CharField(max_length=250)
    rank = models.IntegerField(null=True, blank=True)
    iscsh = models.BooleanField()
    season = models.IntegerField()

class Player(models.Model):
    link = models.CharField(max_length=200)
    name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    picture = models.CharField(max_length=250)
    team = models.ManyToManyField(Team)
    iscaptain = models.BooleanField()

class Matchup(models.Model):
    csh = models.ForeignKey(Team, related_name='CSH')
    enemy = models.ForeignKey(Team, related_name='ENEMY')
    cshScore = models.IntegerField(null=True, blank=True)
    enemyScore = models.IntegerField(null=True, blank=True)
    upcoming = models.CharField(max_length=50, default='')
    outcome = models.CharField(max_length=1, default='')
    date = models.DateTimeField()
    clean_date = models.CharField(max_length=50)

    def __eq__(self, oMatchup):
        return self.csh==oMatchup.csh and self.enemy == oMatchup.enemy and self.clean_date == oMatchup.clean_date


class Authenticate(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    imusername = models.CharField(max_length=20)
    impassword = models.CharField(max_length=20)

class Season(models.Model):
    season = models.IntegerField()
