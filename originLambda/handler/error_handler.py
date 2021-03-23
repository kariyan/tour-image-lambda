from domain.request import *
from service import image_service
from service import message_service
from service.s3_service import LIVE_DISTRIBUTION_ID

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def throw(local_image, request, err_code, err_reason):
    logger.error('an error occurred when getting origin image : {}'.format(request.origin_url))
    logger.error('[ERR] code: {}, message: {}'.format(err_code, err_reason))

    if request.distribution_id == LIVE_DISTRIBUTION_ID:
        user_name = 'LIVE'
    else:
        user_name = 'DEV'

    if err_code == 404:
        result = 'Default Image'
    else:
        result = 'Redirect'

    message = '[{}] An error occurred when getting origin image.\n{}\n- ({}) {}' \
        .format(result, request.origin_url, err_code, err_reason)
    message_service.send(user_name, message)

    if err_code == 404:
        image_service.take_default_image(request, local_image)
    else:
        raise IOError
