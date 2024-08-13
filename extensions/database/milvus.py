from pymilvus import connections, db
from flask import Flask

class Database:
    """
    # Milvus DataBase
    """
    def __init__(self, app: Flask, db_name: str = "default") -> None:
        self.conn = connections.connect(
            uri=app.config.get("MILVUS")['uri'],
            token=app.config.get("MILVUS")['token'],
            db_name=db_name
        )
        self.db = db