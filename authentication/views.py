from django.views.generic import TemplateView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth import views as auth_views

from django.shortcuts import render

from booking.settings import LOGIN_REDIRECT_URL


class NotShibbolethMixin(AccessMixin):
    """Verify that the current user is NOT authenticated through Shibboleth."""
    raise_exception = True
    permission_denied_message = "Operazione non consentita."

    def dispatch(self, request, *args, **kwargs):
        if request.session.get("AUTH_SHIB", False):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class LoginSelector(TemplateView):
    template_name = "registration/login.html"

    def get_context_data(self, activity_id=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.request.GET.get("next", None)
        return context


class LoginSSO(TemplateView):
    template_name = "registration/shiberror.html"

    def get(self, request):
        # If the user is logged in redirect to the correct page
        if request.user.is_authenticated:
            # Mark the user as logged using SSO
            request.session["AUTH_SHIB"] = True
            nextUrl = request.GET.get("next", LOGIN_REDIRECT_URL)
            return HttpResponseRedirect(nextUrl)
        return super().get(request)


class BookingPasswordResetView(NotShibbolethMixin, auth_views.PasswordResetView):
    pass


class BookingPasswordResetDoneView(NotShibbolethMixin, auth_views.PasswordResetDoneView):
    pass


class BookingPasswordResetConfirmView(NotShibbolethMixin, auth_views.PasswordResetConfirmView):
    pass


class BookingPasswordResetCompleteView(NotShibbolethMixin, auth_views.PasswordResetCompleteView):
    pass


class BookingPasswordChangeView(NotShibbolethMixin, auth_views.PasswordChangeView):
    pass


class BookingPasswordChangeDoneView(NotShibbolethMixin, auth_views.PasswordChangeDoneView):
    pass
