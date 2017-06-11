# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from tandlr.registration.models import RegistrationProfile


def confirm(request, activation_key):
    # Get template view
    context = RequestContext(request)
    template_name = 'email/registration/confirm.html'

    # Get registration profile
    register_profile = get_object_or_404(
        RegistrationProfile, activation_key=activation_key)

    context['user_register'] = register_profile.user
    if register_profile.is_activated:
        template_name = 'email/registration/token_used.html'
        return render_to_response(template_name, context_instance=context)

    # Validate confirm email
    if register_profile.key_expired:
        template_name = 'email/registration/token_expired.html'
        return render_to_response(template_name, context_instance=context)

    # Update status key activation

    register_profile.is_activated = True
    register_profile.save()

    return render_to_response(template_name, context)
