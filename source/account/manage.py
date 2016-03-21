from django.db import models


class UserProfileQuerySet(models.Model):
    def get_user_by_email(self, email):
        return self.filter(user_email=email)

    def get_user_by_email_password(self, email, passwd):
        return self.filter(user_email=email, user_password=passwd)


class UserProfileManager(models.Model):
    def get_query_set(self):
        return UserProfileQuerySet(self.model, using=self._db)

    def get_user_by_email(self, email):
        return self.get_query_set().get_user_by_email(email)

    def get_user_by_email_password(self, email, passwd):
        return self.get_query_set().get_user_by_email_password(email, passwd)
