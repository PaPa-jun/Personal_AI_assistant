class Base:
    SECRET_KEY = "you-shall-no-pass"
    ENV = "base"
    MILVUS = {
        "uri": "http://localhost:19530",
        "token": "root:Milvus"
    }
    DEBUG = False
    TESTING = False

class Develop(Base):
    ENV = "development"
    DEBUG = True

class Test(Base):
    ENV = "test"
    TESTING = True

config_map = {
    "default" : Base,
    "develop" : Develop,
    "test" : Test
}