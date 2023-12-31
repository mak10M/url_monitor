
class RequestParser:

    def __init__(self, request):
        self.request = request
        self.urls = []

    def parse_request(self):
        args = self.request.args
        for i in range(1, len(args) + 1):
            self.urls.append(args.get(f'key{i}'))

