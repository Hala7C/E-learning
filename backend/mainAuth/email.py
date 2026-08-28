from djoser import email


class ActivationEmail(email.ActivationEmail):
    template_name = 'email/active_email.html'
    def get_context_data(self):
        context = super().get_context_data()
        context["protocol"] = "http"
        context["domain"] = "localhost:3000"
        context["custom_variable"] = "Custom Value"
        context['custom_variable'] = 'Custom Value'
        # Add other variables to the context dictionary
        return context