import oracledb
from sqlalchemy import create_engine
from .datasource import Datasource

class OracleDatasource(Datasource):
    def __init__(self, mode, username, password, hostname, sid, port=1521, base=None):
        super().__init__()
        self.mode = mode
        self.username = username
        self.password = password
        self.hostname = hostname
        self.sid = sid
        self.port = port
        self.base = base
        self.engine = self.create_connection()
        
        if self.base is not None:
            self.bind_models_to_engine(self.base)
            
        self.session = self.create_session()

    def create_connection(self):
        try:
            dsn_str = oracledb.makedsn(self.hostname, self.port, sid=self.sid)
            if self.mode == "thick":
                connection_string = f"oracle+cx_oracle://{self.username}:{self.password}@{dsn_str}"
            else:
                connection_string = f"oracle+oracledb://{self.username}:{self.password}@{dsn_str}"
            engine = create_engine(connection_string)
            return engine
        except Exception as e:
            raise Exception(f"Error creating connection: {e}")