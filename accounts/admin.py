from django.contrib import admin
from accounts.models import User, Role, ACMMEMBER, GuestUser, MembershipType

admin.site.register(User)
admin.site.register(Role)
admin.site.register(ACMMEMBER)
admin.site.register(GuestUser)
admin.site.register(MembershipType)