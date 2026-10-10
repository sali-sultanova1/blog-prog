from django.core.paginator import Paginator
from django.shortcuts import render

def render_paginated(request, template, queryset, *, context=None, name="articles", per_page=10):
    page = Paginator(queryset, per_page).get_page(request.GET.get("page"))
    page_context = dict(context or {})
    page_context[name] = page.object_list
    page_context["page_obj"] = page

    return render(request, template, page_context)