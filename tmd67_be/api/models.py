from django.db import models


class Agency(models.Model):
    level = models.CharField(max_length=8)
    division = models.CharField(max_length=3)
    area = models.IntegerField(blank=True, null=True)


class Role(models.Model):
    en_title = models.CharField(max_length=255, blank=True, null=True)
    tw_title = models.CharField(max_length=255)


class Member(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    chinese_name = models.CharField(max_length=20)
    email = models.CharField(max_length=60)
    achievement = models.CharField(max_length=50, blank=True, null=True)
    member_no = models.CharField(max_length=20, blank=True, null=True)
    line = models.CharField(max_length=20, blank=True, null=True)


class Club(models.Model):
    agency = models.ForeignKey(Agency, models.CASCADE)
    club_number = models.IntegerField()
    chinese_name = models.CharField(max_length=100)
    english_name = models.CharField(max_length=100)
    charter_date = models.DateField(blank=True, null=True)
    meeting_week = models.CharField(max_length=255, blank=True, null=True)
    meeting_day = models.CharField(max_length=9, blank=True, null=True)
    meeting_start = models.TimeField(blank=True, null=True)
    meeting_end = models.TimeField(blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=255)
    club_type = models.CharField(max_length=9)
    qualification = models.CharField(max_length=8, blank=True, null=True)
    fee = models.CharField(max_length=255, blank=True, null=True)
    abbr = models.CharField(max_length=255, blank=True, null=True)
    photo = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    en_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.IntegerField(blank=True, null=True)
    zipcode = models.IntegerField(blank=True, null=True)
    memo = models.CharField(max_length=255, blank=True, null=True)


class Event(models.Model):
    tw_title = models.CharField(max_length=250)
    en_title = models.CharField(max_length=250, blank=True, null=True)
    member = models.ForeignKey(Member, models.CASCADE)
    contents = models.TextField(blank=True, null=True)
    agenda = models.TextField(blank=True, null=True)
    countdown = models.DateField()
    deadline = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    address = models.CharField(max_length=250, blank=True, null=True)
    address2 = models.CharField(max_length=150, blank=True, null=True)
    vacancy = models.IntegerField()
    standby = models.IntegerField()
    target = models.CharField(max_length=250, blank=True, null=True)
    fee = models.CharField(max_length=150)
    languages = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    cover_photo = models.CharField(max_length=250, blank=True, null=True)
    link = models.CharField(max_length=250, blank=True, null=True)
    memo = models.CharField(max_length=250, blank=True, null=True)


class Attachment(models.Model):
    event = models.ForeignKey(Event, models.CASCADE)
    name = models.CharField(max_length=255)
    attachment = models.CharField(max_length=255)


class Office(models.Model):
    member = models.ForeignKey(Member, models.CASCADE)
    agency = models.ForeignKey(Agency, models.CASCADE)
    club = models.ForeignKey(Club, models.CASCADE, blank=True, null=True)
    role = models.ForeignKey(Role, models.CASCADE)
    print = models.IntegerField(blank=True, null=True)
    batch = models.IntegerField(blank=True, null=True)
    confirm = models.IntegerField(blank=True, null=True)


class Path(models.Model):
    en_name = models.CharField(max_length=255)
    tw_name = models.CharField(max_length=255)
    en_description = models.TextField()
    tw_description = models.TextField()


class Project(models.Model):
    path = models.ForeignKey(Path, models.CASCADE)
    level = models.IntegerField()
    en_name = models.CharField(max_length=255)
    tw_name = models.CharField(max_length=255)
    en_description = models.TextField()
    tw_description = models.TextField()
    en_purpose = models.TextField()
    tw_purpose = models.TextField()
    en_overview = models.TextField()
    tw_overview = models.TextField()
    includes = models.JSONField()
    evaluation_form = models.URLField()
