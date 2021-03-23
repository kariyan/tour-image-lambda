import logging

from enum import Enum
from urllib.parse import parse_qs, urlencode

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    request = event['Records'][0]['cf']['request']
    logger.info("request: {}".format(request))

    params = {k: v[0] for k, v in parse_qs(request['querystring']).items()}
    w, h = params.get('w'), params.get('h')

    if w == '0' and h == '0':
        return __rebuild_querystring(request, params, None)

    for image_spec in ListingImageSpec:
        if w == str(image_spec.value[0]) and h == str(image_spec.value[1]):
            return __rebuild_querystring(request, params, image_spec)

    return __rebuild_querystring(request, params, ListingImageSpec.ORIGINAL)


def __rebuild_querystring(request, params, image_spec):
    if image_spec is None:
        params['w'] = 0
        params['h'] = 0
    else:
        params['w'] = image_spec.value[0]
        params['h'] = image_spec.value[1]

    if params.get('f') is None:
        try:
            if 'image/webp' in request['headers']['accept'][0]['value'].lower():
                params['f'] = 'webp'
        except KeyError:
            pass

    sorted_params = __sort_parameters(params)
    __normalize_querystring(request, sorted_params)

    return request


def __normalize_querystring(request, sorted_params):
    request['querystring'] = urlencode(sorted_params)
    request['cache-control'] = {
        'key': 'Cache-Control',
        'value': 'max-age=31536000'
    }
    logger.info("replaced request : {}".format(request))


def __sort_parameters(params):
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    return sorted_params


class ListingImageSpec(Enum):
    SMALL = (160, 160)
    MEDIUM = (266, 266)
    LARGE = (368, 368)
    WIDE = (580, 320)
    ORIGINAL = (460, 460)
