from django.db import models
from django.contrib.auth.models import User
from oauth2client.django_orm import CredentialsField, FlowField
import six


class GoogleOauth(models.Model):
    user = models.ForeignKey(User, db_index=True)


if six.PY3:
    # Python3 shims.
    # Still need to use add_metaclass, so the python2 parser doesn't break
    # on metaclass=...

    # But - in python2 this breaks.  so double shimmed.
    @add_metaclass(models.SubfieldBase)
    class Py3FlowField(FlowField):
        pass

    @add_metaclass(models.SubfieldBase)
    class Py3CredentialsField(CredentialsField):
        pass

if six.PY2:
    class Py3FlowField(FlowField):
        pass

    class Py3CredentialsField(CredentialsField):
        pass


# These are for the google logins
class CredentialsModel(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    credential = Py3CredentialsField()


class FlowModel(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    flow = Py3FlowField()
