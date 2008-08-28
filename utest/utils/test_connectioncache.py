import unittest
import sys

if __name__ == "__main__":
    sys.path.insert(0, "../../src")
    

from robot.utils.asserts import *
from robot.errors import DataError

from robot.utils import ConnectionCache


class ConnectionMock:
    def __init__(self, id=None):
        self.id = id
        self.closed_by_close = False
        self.closed_by_exit = False
    def close(self):
        self.closed_by_close = True
    def exit(self):
        self.closed_by_exit = True


class TestConnnectionCache(unittest.TestCase):
    
    def setUp(self):
        self.cache = ConnectionCache()
        
    def test_initial(self):
        self._verify_initial_state()
        
    def test_register_one(self):
        conn = ConnectionMock()
        index = self.cache.register(conn)
        assert_equals(index, 1)
        assert_equals(self.cache.current, conn)
        assert_equals(self.cache._connections, [conn])
        assert_equals(self.cache._aliases, {})

    def test_register_multiple(self):
        c1 = ConnectionMock(); c2 = ConnectionMock(); c3 = ConnectionMock()
        for i, conn in enumerate([c1,c2,c3]):
            index = self.cache.register(conn)
            assert_equals(index, i+1)
            assert_equals(self.cache.current, conn)
        assert_equals(self.cache._connections, [c1,c2,c3])
        
    def test_switch_with_index(self):
        self._register('a', 'b', 'c')
        self._assert_current('c', 3)
        self.cache.switch(1)
        self._assert_current('a', 1)
        self.cache.switch('2')
        self._assert_current('b', 2)

    def _assert_current(self, id, index):
        assert_equals(self.cache.current.id, id)
        assert_equals(self.cache.current_index, index)
        
    def test_switch_with_non_existing_index(self):
        self._register('a', 'b')
        assert_raises_with_msg(DataError, "Non-existing index or alias '3'",
                               self.cache.switch, 3)
        assert_raises_with_msg(DataError, "Non-existing index or alias '42'",
                               self.cache.switch, 42)

    def test_register_with_alias(self):
        conn = ConnectionMock()
        index = self.cache.register(conn, 'My Connection')
        assert_equals(index, 1)
        assert_equals(self.cache.current, conn)
        assert_equals(self.cache._connections, [conn])
        assert_equals(self.cache._aliases, { 'myconnection' : 1 })

    def test_register_multiple_with_alis(self):
        c1 = ConnectionMock(); c2 = ConnectionMock(); c3 = ConnectionMock()
        for i, conn in enumerate([c1,c2,c3]):
            index = self.cache.register(conn, 'c%d' % (i+1))
            assert_equals(index, i+1)
            assert_equals(self.cache.current, conn)
        assert_equals(self.cache._connections, [c1,c2,c3])
        assert_equals(self.cache._aliases, {'c1' : 1, 'c2' : 2, 'c3' : 3 })
        
    def test_switch_with_alias(self):
        self._register('a', 'b', 'c', 'd', 'e')
        assert_equals(self.cache.current.id, 'e')
        self.cache.switch('a')
        assert_equals(self.cache.current.id, 'a')
        self.cache.switch('C')
        assert_equals(self.cache.current.id, 'c')
        self.cache.switch('  B   ')
        assert_equals(self.cache.current.id, 'b')
        
    def test_switch_with_non_existing_alias(self):
        self._register('a', 'b')
        assert_raises_with_msg(DataError, "Non-existing index or alias 'whatever'",
                               self.cache.switch, 'whatever')
                
    def test_switch_with_alias_overriding_index(self):
        self._register('2', '1')
        self.cache.switch(1)
        assert_equals(self.cache.current.id, '2')
        self.cache.switch('1')
        assert_equals(self.cache.current.id, '1')
        
    def test_close_all(self):
        connections = self._register('a', 'b', 'c', 'd')
        self.cache.close_all()
        self._verify_initial_state()
        for conn in connections:
            assert_true(conn.closed_by_close)
            
    def test_close_all_with_given_method(self):
        connections = self._register('a', 'b', 'c', 'd')
        self.cache.close_all('exit')
        self._verify_initial_state()
        for conn in connections:
            assert_true(conn.closed_by_exit)
            
    def test_empty_cache(self):
        connections = self._register('a', 'b', 'c', 'd')
        self.cache.empty_cache()
        self._verify_initial_state()
        for conn in connections:
            assert_false(conn.closed_by_close)
            assert_false(conn.closed_by_exit)
        
    def _verify_initial_state(self):
        assert_none(self.cache.current)
        assert_none(self.cache.current_index)
        assert_equals(self.cache._connections, [])
        assert_equals(self.cache._aliases, {})

    def _register(self, *ids):
        connections = []
        for id in ids:
            conn = ConnectionMock(id)
            self.cache.register(conn, id)
            connections.append(conn)
        return connections

if __name__ == '__main__':
    unittest.main()
  