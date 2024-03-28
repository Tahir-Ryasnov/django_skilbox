import time
from django.http import HttpRequest
from requestdataapp.exceptions import AdminException

IP_LIST = list()
TIME = 60
MAX_REQ = 100


def set_useragent_on_request_middleware(get_response):
    print('Initial call')

    def middleware(request: HttpRequest):
        # print('before get_response')
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        # print('after get_response')
        return response

    return middleware


class CountRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.responses_count = 0
        self.requests_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.requests_count += 1
        # print(f'requests count = {self.requests_count}')
        response = self.get_response(request)
        self.responses_count += 1
        # print(f'responses_count = {self.responses_count}')
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print(f'exceptions count = {self.exceptions_count}')


def throttling_middleware(get_response):
    def _get_ip_address(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        return ip_address

    def middleware(request: HttpRequest):

        ip_address = _get_ip_address(request)
        _ip = next((el for el in IP_LIST if el['ip_address'] == ip_address), False)
        if not _ip:
            time_now = time.time()
            IP_LIST.append({'ip_address': ip_address, 'count': 1, 'time': time_now})
        else:
            time_now = time.time()
            if time_now - _ip['time'] > TIME:
                new_list = [el for el in IP_LIST if not el == _ip]
                return new_list
            else:
                _ip['count'] += 1
                if _ip['count'] >= MAX_REQ:
                    raise AdminException('Too Many Requests')
                return get_response(request)
        return get_response(request)
    return middleware


















