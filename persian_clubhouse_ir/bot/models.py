from django.db import models


class Profile(models.Model):
    telegram_user_id = models.CharField(primary_key=True, max_length=250)
    telegram_username = models.CharField(max_length=250, db_index=True)
    telegram_name = models.CharField(max_length=250)

    clubhouse_user_id = models.CharField(max_length=250, db_index=True, null=True)
    clubhouse_username = models.CharField(max_length=250, db_index=True, null=True)
    clubhouse_phone_number = models.CharField(max_length=13, db_index=True)
    clubhouse_auth_token = models.CharField(max_length=350)

    instagram_username = models.CharField(max_length=350)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
