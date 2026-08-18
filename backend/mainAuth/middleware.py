from django.utils.translation import activate

class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract language code from the URL
        language_code = request.path_info.split('/')[1]

        # Activate the language
        activate(language_code)

        response = self.get_response(request)

        return response