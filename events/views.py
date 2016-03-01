from django.shortcuts import render
from django.views.generic import TemplateView


class ExampleView(TemplateView):
    template_name = "events/example.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extra_data"] = [1, 1, 2, 3, 5, 8, 13, 21]
        return context
