import logging
import ssl
import urllib.request
import uuid

from PIL import Image
from resizeimage import resizeimage

logger = logging.getLogger()


class LocalImage:
    def __init__(self):
        self.is_default_image = False
        self.uuid_key = uuid.uuid4()
        self.source_path = '/tmp/{}'.format(self.uuid_key)
        self.transform_path = '/tmp/{}-resized'.format(self.uuid_key)

    def take_from(self, origin_url):
        logger.info('download an image from origin site : {}'.format(origin_url))
        req = urllib.request.Request(origin_url, headers={'User-Agent': 'Mozilla/5.0'})
        context = ssl.SSLContext()
        response = urllib.request.urlopen(req, context=context).read()
        with open(self.source_path, 'wb') as file:
            file.write(response)

    def resize(self, resizing_request):
        with Image.open(self.source_path) as image:
            if resizing_request.width != 0 and resizing_request.height != 0:
                height, width = LocalImage.__limit_max_size(image, resizing_request.height, resizing_request.width)

                logger.info('resize the image : {} X {}'.format(width, height))
                resized_image = resizeimage.resize_cover(image, (width, height))
                LocalImage.__save_image(resized_image, self.transform_path, resizing_request.image_format)
            else:
                self.change_format(resizing_request.image_format)

    def change_format(self, image_format):
        with Image.open(self.source_path) as image:
            LocalImage.__save_image(image, self.transform_path, image_format)

    def set_default_image(self, is_default_image):
        self.is_default_image = is_default_image

    def is_default_image(self):
        return self.is_default_image

    @staticmethod
    def __limit_max_size(image, height, width):
        if width > image.size[0]:
            width = image.size[0]
        if height > image.size[1]:
            height = image.size[1]
        return height, width

    @staticmethod
    def __save_image(image, target_path, image_format):
        if image_format not in ['png', 'webp', 'gif']:
            image = image.convert('RGB')
        image.save(target_path, format(image_format))
        logger.info('image process is completed. format : {}, size : {}'.format(image_format, image.size))
