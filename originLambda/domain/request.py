import logging
from urllib import parse

logger = logging.getLogger()


class Request:
    def __init__(self, event):
        self.distribution_id = event['Records'][0]['cf']['config']['distributionId']
        self.request = event['Records'][0]['cf']['request']
        logger.info('request : {}'.format(self.request))

        params = {k: v[0] for k, v in parse.parse_qs(self.request['querystring']).items()}

        self.width, self.height, self.image_format = 0, 0, 'jpeg'
        self.origin_url = params.get('url', None)
        if self.origin_url is not None:
            self.encoded_url = parse.quote(self.origin_url, '', 'utf8')

        if 'w' in params:
            self.width = int(params['w'])
        if 'h' in params:
            self.height = int(params['h'])
        if 'f' in params:
            self.image_format = params['f']

    def get(self, name):
        return self.request.get(name, None)

    def is_favicon(self):
        return self.request.get('uri') == '/favicon.ico'

    def get_resizing_request(self):
        return ResizingRequest(self.width, self.height, self.image_format)


class ResizingRequest:
    def __init__(self, width, height, image_format):
        self.width, self.height, self.image_format = width, height, image_format
