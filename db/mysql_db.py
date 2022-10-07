from enum import Enum
from typing import Optional
from mysql import connector

class Error(Enum):
    OK = (0, 'Успешно')
    SECRET_NAME_ALREADY_EXISTS = (1, 'Название уже занято')
    LONG_NAME = (2, 'Название должно быть меньше 100 символов')
    SECRET_DOES_NOT_EXISTS = (3, 'Данного аккаунта не существует')
    
    def __init__(self, code, message):
        self.code = code
        self.message = message
    

class DB:
    def __init__(
            self, host: str, user: str,
            password: str, database: str
        ) -> None:
        try:
            self.connection = connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
        except connector.Error as e:
            print(e)
            raise Exception('Can\'t connect to database')
        
    def __del__(self):
        if self.connection.is_connected():
            self.connection.close()
        
    def get_secret(self, user_id: int, name: str) -> Optional[str]:
        query = """
        SELECT secret 
        FROM secrets
        WHERE user_id = %s AND name = %s
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, (user_id, name,))
            
            secret = cursor.fetchone()
            return None if secret is None else secret[0]
        
    def get_user_secrets_name(self, user_id: int) -> list[str]:
        query = """
        SELECT name 
        FROM secrets
        WHERE user_id = %s
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, (user_id,))
            
            names = cursor.fetchall()
            return [] if names is None else list(name[0] for name in names)
        
    def set_secret(self, user_id: int, name: str, secret: str) -> Error:
        if (len(name) >= 100):
            return Error.LONG_NAME
        
        secrets = self.get_user_secrets_name(user_id)
        
        if secrets is not None and name in secrets:
            return Error.SECRET_NAME_ALREADY_EXISTS
        
        query = """
        INSERT INTO secrets
        VALUES (%s, %s, %s)
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, (user_id, name, secret,))
            self.connection.commit()
            
        return Error.OK
    
    def delete_secret(self, user_id: int, name: str) -> Error:
        secret = self.get_secret(user_id, name)
        if secret is None:
            return Error.SECRET_DOES_NOT_EXISTS
        
        query = """
        DELETE FROM secrets
        WHERE user_id = %s AND name = %s
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, (user_id, name,))
            self.connection.commit()
        
        return Error.OK
            
    def is_exist(self, user_id: int, name: str) -> bool:
        return self.get_secret(user_id, name) is not None
