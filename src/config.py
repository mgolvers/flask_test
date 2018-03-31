# config.py


class Config(object):
    """ Common configuration  """
    # Put here all env config
    Debug = True


class DevelopmentConfig(Config):
    """ Development configuration """
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """ Production configuration """
    DEBUG = False


class TestingConfig(Config):
    """ Testing configuration """
    TESTING = True


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
