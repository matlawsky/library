from django.contrib.auth.models import AbstractUser
from django.db import models

# custom user model
# I created custom user model but in fact
# I decided to use profile approach and any additional user data
# like copies in posession and account balance will be held seperate


class CustomUser(AbstractUser):
    pass
