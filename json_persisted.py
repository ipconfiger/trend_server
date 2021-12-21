# coding: utf-8

import logging
import pickledb
from pydantic import BaseModel
from uuid import uuid4


class TestType(BaseModel):
    id: str
    name: str
    age: int


class JsonDatabase(object):
    databases = {}

    @classmethod
    def byDatabaseName(cls, name: str):
        if name in cls.databases:
            return cls.databases[name]
        db = cls(name)
        cls.databases[name] = db
        return db

    def __init__(self, name):
        self.name = name
        self.db = pickledb.load(f'{name}.db', False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            logging.error(f'<{exc_type}>{exc_val}:{exc_tb}')
        else:
            self.db.dump()

    def set(self, key: str, obj: BaseModel):
        tp = str(obj.__class__)
        real_key = f'<{tp}>{key}'
        self.db.set(real_key, obj.json())

    def get(self, key: str, cls):
        tp = str(cls)
        real_key = f'<{tp}>{key}'
        data = self.db.get(real_key)
        if data:
            return cls.parse_raw(data)

    def by_type(self, cls):
        tp = str(cls)
        for key in self.db.getall():
            if tp in key:
                data = self.db.get(key)
                yield cls.parse_raw(data)

    def rem(self, key: str, cls):
        tp = str(cls)
        real_key = f'<{tp}>{key}'
        self.db.rem(real_key)



def test():
    with JsonDatabase.byDatabaseName('test_chn') as db:
        testData = TestType(id=uuid4().hex, name='hahahah', age=33)
        db.set(testData.id, testData)
        print(db.get(testData.id, TestType))


if __name__ == '__main__':
    test()
