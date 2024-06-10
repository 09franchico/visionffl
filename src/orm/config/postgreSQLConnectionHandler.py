from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

class PostgreSQLConnectionHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgreSQLConnectionHandler, cls).__new__(cls)
            
            host = "localhost"
            port = 5432
            user = "postgres"
            password = "1234"
            dbname = "visionffl"

            password_encoded = quote_plus(password)
            connection_string = f'postgresql://{user}:{password_encoded}@{host}:{port}/{dbname}'
            cls._connection = create_engine(connection_string, echo=True)
            cls._Session = sessionmaker(bind=cls._connection)
        return cls._instance

    def __init__(self):
        self.__engine = self._connection
        self.session = None

    def get_engine(self):
        return self.__engine
    
    def dispose(self):
        self.__engine.dispose()

    def __enter__(self):
        self.session = self._Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()