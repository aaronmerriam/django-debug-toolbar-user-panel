from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.conf import settings
from django.contrib import auth
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from .forms import UserForm

def content(request):
    current = []

    if request.user.is_authenticated():
        for field in User._meta.fields:
            if field.name == 'password':
                continue
            current.append(
                (field.attname, getattr(request.user, field.attname))
            )

    return render_to_response('debug_toolbar_user_panel/content.html', {
        'form': UserForm(),
        'next': request.GET.get('next'),
        'users': User.objects.order_by('-last_login')[:10],
        'current': current,
        'enabled': request.session.get('debug_toolbar_user_panel_enabled', False),
    }, context_instance=RequestContext(request))

@csrf_exempt
@require_POST
def login_form(request):
    if not request.session.get('debug_toolbar_user_panel_enabled', False):
        raise PermissionDenied
    form = UserForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest()

    return login(request, **form.get_lookup())

@csrf_exempt
@require_POST
def login(request, **kwargs):
    if not request.session.get('debug_toolbar_user_panel_enabled', False):
        raise PermissionDenied
    user = get_object_or_404(User, **kwargs)

    user.backend = settings.AUTHENTICATION_BACKENDS[0]
    auth.login(request, user)

    return HttpResponseRedirect(request.POST.get('next', '/'))
