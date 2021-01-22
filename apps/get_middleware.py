# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)


class StripContentTypeMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'GET':
            if "CONTENT_TYPE" in environ:
                del environ['CONTENT_TYPE']
                logger.debug('Remove header "Content-Type" from GET request')
        return self.app(environ, start_response)
