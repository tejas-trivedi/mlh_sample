from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import RegexValidator
from django.db import models
from rest_framework.authtoken.models import Token
import secrets
import string

class Role(models.Model):

    SUPER_ADMIN = 1
    ACM_MEMBER = 2
    GUEST = 3

    ROLE_CHOICES = (
        (SUPER_ADMIN, 'super_admin'),
        (ACM_MEMBER, 'acm_member'),
        (GUEST, 'guest'),
    )

    id = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):
        return self.get_id_display()


class UserManager(BaseUserManager):
    """
        CUSTOM UserManager To handle user creation and superuser creation.
        INITIALLY 2 methods

        1- create_user() accepts all parameters which are REQUIRED_FIELDS
        2- create_superuser() to create a SuperUser

        **WARNING**: In create_user roles for specific user will be set after User has been saved to database and we have to use set(). Which accepts list of args eg: set([value])
    """

    def create(self, email_id, roles, password='None'):
        if not email_id:
            raise ValueError('Email ID must be set')
        if not roles:
            raise ValueError('Roles must be set')

        user = self.model(email_id=email_id)
        user.set_password(password)
        user.save(using=self._db)
        user.roles.set([roles])
        return user

# roles
    def create_user(self, email_id, roles, password='None'):
        if roles is None:
            roles = 3
        if not email_id:
            raise ValueError('Email ID must be set')

        if not password:
            raise ValueError('Password must be set')
        roles = Role.objects.get(id=roles)
        print(roles)
        # pass fields as arguments which are REQUIRED_FIELDS to user = self.model()
        user = self.model(email_id=email_id)
        # user.set_password(password) to change the password
        user.set_password(password)
        user.save(using=self._db)
        # user.roles.set([roles])
        return user

    def create_superuser(self, email_id, password):
        roles = 1
        user = self.create_user(
            email_id,
            roles,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    
    email_id = models.CharField(
        max_length=100, unique=True, null=False, blank=False) # unique=True
    roles = models.ManyToManyField(Role,  default=3)
    is_active = models.BooleanField(default=True, null=False, blank=False)
    is_staff = models.BooleanField(default=False, null=False, blank=False)
    is_superuser = models.BooleanField(default=False, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email_id'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email_id

    def get_full_name(self):
        return self.email_id


class ACMMEMBER(models.Model):

    BRANCHES = (
        ("None", "Choose an option"),
        ("CSE BAO", "CSE BAO"),
        ("CSE AIML", "CSE AIML"),
        ("CSE CCVT", "CSE CCVT"),
        ("CSE CSF", "CSE CSF"),
        ("CSE IT-INFRA", "CSE IT-INFRA"),
    )

    YEAR = (
        ("None", "Choose your Year"),
        ("1st Year", "1st Year"),
        ("2nd Year", "2nd Year"),
        ("3rd Year", "3rd Year"),
        ("4th Year", "4th Year"),
    )

    MEMBERSHIP = (
        ("None", "Choose an option"),
        ("Premium (4 Years + 1 Year International)",
         "Premium (4 Years + 1 Year International)"),
        ("Standard (2 Years)", "Standard (2 Years)"),
        ("Basic (1 Year)", "Basic (1 Year)"),
    )
    member = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, null=False, blank=False)
    branch = models.CharField(choices=BRANCHES, default='None', max_length=100)
    year = models.CharField(choices=YEAR, default='None', max_length=20)
    
    dob = models.DateField(null=True)
    dob = models.DateField(null=True)
    contact_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$", message="Phone number must be entered in the format: '+919939799264'. Up to 15 digits allowed.",)
    contact_number = models.CharField(
        validators=[contact_regex], max_length=15)  # , unique=True)
    whatsapp_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$", message="Phone number must be entered in the format: '+919939799264'. Up to 15 digits allowed.",)
    whatsapp_number = models.CharField(
        validators=[whatsapp_regex], max_length=15)  # , unique=True)
    sap_id = models.CharField(max_length=9, null=False,
                              blank=False)
    hostel_pg = models.TextField()
    membership_type = models.ForeignKey(
        'MembershipType',  on_delete=models.CASCADE, default='None')
    is_active = models.BooleanField(default=True, null=False, blank=False)
    is_staff = models.BooleanField(default=False, null=False, blank=False)
    is_superuser = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return (f"Email ID: {self.member}")


class GuestUser(models.Model):
    made_on = models.DateTimeField(auto_now_add=True)
    guest_id = models.CharField(
        unique=True, max_length=100, null=True, blank=True)
    guest_name = models.CharField(
        default='None', max_length=20, null=True, blank=False)
    guest_email = models.EmailField(
        max_length=30, null=False, blank=False)

    def save(self, *args, **kwargs):
        if self.guest_id is None and self.made_on and self.id:
            self.guest_id = str(secrets.token_urlsafe(16)) + \
                str(secrets.token_hex(6))
        return super().save(*args, **kwargs)
    
    
class MembershipType(models.Model):
    MEMBERSHIP = models.CharField(
        unique=True, max_length=100, primary_key=True, default='None')
    Price = models.IntegerField()
    Duration = models.IntegerField()

    def price(self):
        return self.Price


    def __str__(self):
        return self.MEMBERSHIP
