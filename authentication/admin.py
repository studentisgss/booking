from django.contrib import admin
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied

# Register your models here.


class BookingUserAdmin(UserAdmin):
    # Add action to diable password login
    actions = ['make_unusable_password']

    def make_unusable_password(self, request, queryset):
        count = 0
        for u in queryset:
            u.set_unusable_password()
            u.save()
            count += 1
        if count == 1:
            message_bit = "1 utente"
        else:
            message_bit = "%d utenti" % count
        self.message_user(request,
                          "Login con password disabilitato per %s con successo." % message_bit)

    make_unusable_password.short_description = "Disabilita login con password"

    # Add button to disable password login
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Show set_unusable_password button
        if extra_context is None:
            extra_context = {}
        extra_context["show_set_unusable_password"] = True

        # If set_unusable button is clicked set unusable password for the user
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        if request.method == 'POST' and '_unusablepassword' in request.POST:
            u = self.get_object(request, unquote(object_id), to_field)
            if not self.has_change_permission(request, u):
                raise PermissionDenied

            u.set_unusable_password()
            u.save()

        # Return the parent class changeform_view
        return super().changeform_view(request, object_id, form_url, extra_context)


admin.site.unregister(User)
admin.site.register(User, BookingUserAdmin)
