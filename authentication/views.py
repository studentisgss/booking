from django.views.generic import TemplateView
from django.http import Http404, HttpResponseRedirect

from django.shortcuts import render

from booking.settings import LOGIN_REDIRECT_URL


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
            nextUrl = request.GET.get("next", LOGIN_REDIRECT_URL)
            return HttpResponseRedirect(nextUrl)
        return super().get(request)
