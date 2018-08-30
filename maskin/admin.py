from django.contrib import admin
from . import models
from django.utils.translation import ugettext_lazy as _

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'rfid' )
    list_display = ('user', 'get_name', 'program', 'start_year' )
    list_filter = ('program', 'start_year')

    def get_name(self, obj):
        return obj.user.first_name +' '+ obj.user.last_name
    get_name.admin_order_field  = 'user'  #Allows column order sorting
    get_name.short_description = _('Name')  #Renames column head


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start', 'end')


class SignupAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'timestamp')


admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.SchoolYear)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Signup, SignupAdmin)
