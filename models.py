# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=240, unique=True)
    class Meta:
        db_table = u'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.IntegerField()
    permission_id = models.IntegerField()
    class Meta:
        db_table = u'auth_group_permissions'

class AuthMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    message = models.TextField()
    class Meta:
        db_table = u'auth_message'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=300, unique=True)
    class Meta:
        db_table = u'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=90, unique=True)
    first_name = models.CharField(max_length=90)
    last_name = models.CharField(max_length=90)
    email = models.CharField(max_length=225)
    password = models.CharField(max_length=384)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    is_superuser = models.IntegerField()
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    class Meta:
        db_table = u'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    group_id = models.IntegerField()
    class Meta:
        db_table = u'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    permission_id = models.IntegerField()
    class Meta:
        db_table = u'auth_user_user_permissions'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)
    app_label = models.CharField(max_length=300, unique=True)
    model = models.CharField(max_length=300, unique=True)
    class Meta:
        db_table = u'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(max_length=120, primary_key=True)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        db_table = u'django_session'

class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.CharField(max_length=300)
    name = models.CharField(max_length=150)
    class Meta:
        db_table = u'django_site'

class SportsMatchup(models.Model):
    id = models.IntegerField(primary_key=True)
    csh_id = models.IntegerField()
    enemy_id = models.IntegerField()
    cshscore = models.IntegerField(null=True, db_column='cshScore', blank=True) # Field name made lowercase.
    enemyscore = models.IntegerField(null=True, db_column='enemyScore', blank=True) # Field name made lowercase.
    upcoming = models.CharField(max_length=150)
    outcome = models.CharField(max_length=3)
    date = models.CharField(max_length=150)
    class Meta:
        db_table = u'sports_matchup'

class SportsPlayer(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    gender = models.CharField(max_length=3)
    picture = models.CharField(max_length=750)
    team_id = models.IntegerField()
    class Meta:
        db_table = u'sports_player'

class SportsTeam(models.Model):
    id = models.IntegerField(primary_key=True)
    link = models.CharField(max_length=600)
    sport = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    wins = models.IntegerField()
    losses = models.IntegerField()
    ties = models.IntegerField()
    picture = models.CharField(max_length=750)
    class Meta:
        db_table = u'sports_team'

