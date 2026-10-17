"""Durable SQLite connections and an atomic unit of work for Activity actions.

Engines keep their existing local transaction boundaries as savepoints. Only
the outer action commits, including its idempotency receipt. PostgreSQL mode
does not use this Activity-only unit of work.
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from contextvars import ContextVar

_unit = ContextVar('activity_sqlite_unit', default=None)

class DurableConnection(sqlite3.Connection):
    def __exit__(self, *exc):
        try:
            return super().__exit__(*exc)
        finally:
            self.close()

class Lease:
    def __init__(self, connection):
        self.connection = connection
        self.savepoint = None
    @property
    def row_factory(self): return self.connection.row_factory
    @row_factory.setter
    def row_factory(self, value): self.connection.row_factory = value
    def __enter__(self):
        self.savepoint = 'lease_' + str(id(self))
        self.connection.execute('SAVEPOINT ' + self.savepoint)
        return self
    def __exit__(self, kind, error, trace):
        if kind: self.rollback()
        self.connection.execute('RELEASE SAVEPOINT ' + self.savepoint)
        self.savepoint = None
        return False
    def execute(self, sql, parameters=()):
        if sql.strip().upper() in ('BEGIN', 'BEGIN IMMEDIATE', 'BEGIN TRANSACTION'):
            return self.connection.execute('SELECT 1')
        return self.connection.execute(sql, parameters)
    def executemany(self, *args): return self.connection.executemany(*args)
    def cursor(self, *args, **kwargs): return self.connection.cursor(*args, **kwargs)
    def commit(self): pass  # The outer action owns the durable commit.
    def rollback(self):
        if self.savepoint: self.connection.execute('ROLLBACK TO SAVEPOINT ' + self.savepoint)
        else: raise RuntimeError('Rollback outside an engine savepoint')
    def close(self): pass  # A lease does not own the outer connection.
    def __getattr__(self, name): return getattr(self.connection, name)

def connect(database, *args, **kwargs):
    path = str(Path(database).resolve())
    active = _unit.get()
    if active and active[0] == path: return Lease(active[1])
    kwargs.setdefault('timeout', 30)
    kwargs.setdefault('factory', DurableConnection)
    c = sqlite3.connect(database, *args, **kwargs)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA busy_timeout=30000')
    c.execute('PRAGMA synchronous=FULL')
    return c

@contextmanager
def atomic(database):
    if _unit.get(): raise RuntimeError('Nested Activity action')
    c = connect(database)
    c.execute('BEGIN IMMEDIATE')
    token = _unit.set((str(Path(database).resolve()), c))
    try:
        yield c
        c.commit()
    except BaseException:
        c.rollback()
        raise
    finally:
        _unit.reset(token)
        c.close()
