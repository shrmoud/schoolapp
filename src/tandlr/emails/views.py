from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template import TemplateDoesNotExist
from django.views.generic.base import TemplateView

from tandlr.scheduled_classes.models import Class


class StaticEmailView(TemplateView):
    """
    View to render static email templates for development.

    example:
    tandlr.local/email-preview/registration/confirmation_email.html
    """
    def get_template_names(self):
        return 'email/%s' % self.kwargs['page']

    def get(self, request, page):
        try:
            return self.render_to_response(self.get_context_data())

        except TemplateDoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super(StaticEmailView, self).get_context_data(**kwargs)

        if self.request.GET.get('session_id'):
            context['booking'] = get_object_or_404(
                Class,
                id=self.request.GET.get('session_id')
            )

        return context
