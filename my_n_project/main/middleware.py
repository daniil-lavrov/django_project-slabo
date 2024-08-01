import time
from django.http import HttpResponse

class ParseStopper:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if 'list_of_req' not in request.session:
            request.session['list_of_req'] = []

        current_time = time.time()

        refresh_list = [item for item in request.session['list_of_req'] if current_time - item <= 60]

        if len(refresh_list) <= 15:
            refresh_list.append(current_time)
            request.session['list_of_req'] = refresh_list
            request.session.modified = True
        else:
            request.session['list_of_req'] = refresh_list
            request.session.modified = True
            return HttpResponse("Too Many Requests", status=429)

        response = self.get_response(request)
        return response
