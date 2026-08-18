from rest_framework.renderers import TemplateHTMLRenderer

class CustomLockoutRenderer(TemplateHTMLRenderer):
    template_name = 'lockout_template.html'