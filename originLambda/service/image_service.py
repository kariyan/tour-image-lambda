from urllib.error import URLError, HTTPError

from domain.image import LocalImage
from domain.request import *
from handler import error_handler
from service.s3_service import S3ImageService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def retrieve_image(request):
    local_image = LocalImage()
    s3_image_service = S3ImageService.from_url(request.distribution_id, request.origin_url, request.encoded_url)

    if s3_image_service.is_image_exists():
        s3_image_service.download(local_image.source_path)
    else:
        try:
            local_image.take_from(request.origin_url)
            if request.origin_url.startswith('https://tourimg.') or request.origin_url.startswith('http://tourimg.'):
                logger.info('(TOUR image is not going to upload)')
            else:
                local_image.change_format('webp')
                s3_image_service.upload(local_image.transform_path)

        except HTTPError as e:
            error_handler.throw(local_image, request, e.code, e.reason)
        except URLError as e:
            error_handler.throw(local_image, request, e.errno, e.reason)

    return local_image


def take_default_image(request, local_image):
    if request.width == request.height:
        default_image = 'vendor/default-square.png'
    else:
        default_image = 'vendor/default-rectangle.png'

    logger.info('get a default image: [{}]'.format(default_image))
    s3_image_service = S3ImageService(request.distribution_id, default_image)
    s3_image_service.download(local_image.source_path)
    local_image.set_default_image(True)
    request.image_format = 'png'
