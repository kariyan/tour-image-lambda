import base64
import copy
import logging
from io import BytesIO

from PIL import Image
from service.s3_service import PATH

logger = logging.getLogger()


def origin(event):
    response = event['Records'][0]['cf']['response']
    logger.info('response : {}'.format(response))
    return response


def image(image_path, img_format, is_default_image):
    with Image.open(image_path) as image_ref:
        logger.info('image size : {}'.format(image_ref.size))

        if is_default_image:
            max_age = 10
        else:
            max_age = 31536000

        buffered = BytesIO()
        image_ref.save(buffered, format=img_format)
        base64_encoded_body = base64.b64encode(buffered.getvalue()).decode('utf-8')
        response = {
            'headers': {
                'transfer-encoding': [
                    {
                        'key': 'Transfer-Encoding',
                        'value': 'chunked'
                    }
                ],
                'cache-control': [
                    {
                        'key': 'Cache-Control',
                        'value': 'max-age=' + str(max_age)
                    }
                ],
                'content-type': [
                    {
                        'key': 'Content-Type',
                        'value': 'image/' + img_format
                    }
                ],
            },
            'body': base64_encoded_body,
            'bodyEncoding': 'base64',
            'status': '200',
            'statusDescription': 'OK'
        }
        replaced_response = copy.deepcopy(response)
        replaced_response['body'] = '...'
        logger.info('response : {}'.format(replaced_response))
        return response


def error__query_parameter_required():
    response = {
        'headers': {
            'transfer-encoding': [
                {
                    'key': 'Transfer-Encoding',
                    'value': 'chunked'
                }
            ],
        },
        'status': '400',
        'statusDescription': 'url query parameter is required.'
    }
    logger.info('response : {}'.format(response))
    return response


def error__illegal_path_parameter():
    response = {
        'headers': {
            'transfer-encoding': [
                {
                    'key': 'Transfer-Encoding',
                    'value': 'chunked'
                }
            ],
        },
        'status': '400',
        'statusDescription': 'request path must start with "/{}".'.format(PATH)
    }
    logger.info('response : {}'.format(response))
    return response


def error__redirection(origin_url):
    response = {
        'headers': {
            'transfer-encoding': [
                {
                    'key': 'Transfer-Encoding',
                    'value': 'chunked'
                },
            ],
            'location': [{
                'key': 'Location',
                'value': origin_url
            }]
        },
        'status': '302',
        'statusDescription': 'Found'
    }
    logger.info('response : {}'.format(response))
    return response
