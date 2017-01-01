# config.py


class Config(object):
    """ Common configuration  """
    # Put here all env config


class DevelopmentConfig(Config):
    """ Development configuration """
    Debug = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """ Production configuration """
    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
