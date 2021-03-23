from domain import response
from domain.request import *
from service import image_service
from service.s3_service import PATH

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    request = Request(event)
    if request.is_favicon():
        return response.origin(event)

    if request.request['uri'] != '/{}'.format(PATH):
        return response.error__illegal_path_parameter()

    if request.origin_url is None:
        return response.error__query_parameter_required()

    try:
        local_image = image_service.retrieve_image(request)
        local_image.resize(request.get_resizing_request())
        return response.image(local_image.transform_path, request.image_format, local_image.is_default_image)
    except IOError:
        return response.error__redirection(request.origin_url)
