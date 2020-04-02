import unittest

from robot.utils.asserts import (assert_equal, assert_false, assert_true,
                                 assert_raises, assert_raises_with_msg)


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

    def __eq__(self, other):
        return hasattr(other, 'id') and self.id == other.id


class TestConnectionCache(unittest.TestCase):

    def setUp(self):
        self.cache = ConnectionCache()

    def test_initial(self):
        self._verify_initial_state()

    def test_no_connection(self):
        assert_raises_with_msg(RuntimeError, 'No open connection.', getattr,
                               ConnectionCache().current, 'whatever')
        assert_raises_with_msg(RuntimeError, 'Custom msg', getattr,
                               ConnectionCache('Custom msg').current, 'xxx')

    def test_register_one(self):
        conn = ConnectionMock()
        index = self.cache.register(conn)
        assert_equal(index, 1)
        assert_equal(self.cache.current, conn)
        assert_equal(self.cache.current_index, 1)
        assert_equal(self.cache._connections, [conn])
        assert_equal(self.cache._aliases, {})

    def test_register_multiple(self):
        conns = [ConnectionMock(1), ConnectionMock(2), ConnectionMock(3)]
        for i, conn in enumerate(conns):
            index = self.cache.register(conn)
            assert_equal(index, i+1)
            assert_equal(self.cache.current, conn)
            assert_equal(self.cache.current_index, i+1)
        assert_equal(self.cache._connections, conns)

    def test_register_multiple_equal_objects(self):
        conns = [ConnectionMock(1), ConnectionMock(1), ConnectionMock(1)]
        for i, conn in enumerate(conns):
            index = self.cache.register(conn)
            assert_equal(index, i+1)
            assert_equal(self.cache.current, conn)
            assert_equal(self.cache.current_index, i+1)
        assert_equal(self.cache._connections, conns)

    def test_register_multiple_same_object(self):
        conns = [ConnectionMock()] * 3
        for i, conn in enumerate(conns):
            index = self.cache.register(conn)
            assert_equal(index, i+1)
            assert_equal(self.cache.current, conn)
            assert_equal(self.cache.current_index, 1)
        assert_equal(self.cache._connections, conns)

    def test_set_current_index(self):
        self.cache.current_index = None
        assert_equal(self.cache.current_index, None)
        self._register('a', 'b')
        self.cache.current_index = 1
        assert_equal(self.cache.current_index, 1)
        assert_equal(self.cache.current.id, 'a')
        self.cache.current_index = None
        assert_equal(self.cache.current_index, None)
        assert_equal(self.cache.current, self.cache._no_current)
        self.cache.current_index = 2
        assert_equal(self.cache.current_index, 2)
        assert_equal(self.cache.current.id, 'b')

    def test_set_invalid_index(self):
        assert_raises(IndexError, setattr, self.cache, 'current_index', 1)

    def test_switch_with_index(self):
        self._register('a', 'b', 'c')
        self._assert_current('c', 3)
        self.cache.switch(1)
        self._assert_current('a', 1)
        self.cache.switch('2')
        self._assert_current('b', 2)

    def _assert_current(self, id, index):
        assert_equal(self.cache.current.id, id)
        assert_equal(self.cache.current_index, index)

    def test_switch_with_non_existing_index(self):
        self._register('a', 'b')
        assert_raises_with_msg(RuntimeError, "Non-existing index or alias '3'.",
                               self.cache.switch, 3)
        assert_raises_with_msg(RuntimeError, "Non-existing index or alias '42'.",
                               self.cache.switch, 42)

    def test_register_with_alias(self):
        conn = ConnectionMock()
        index = self.cache.register(conn, 'My Connection')
        assert_equal(index, 1)
        assert_equal(self.cache.current, conn)
        assert_equal(self.cache._connections, [conn])
        assert_equal(self.cache._aliases, {'myconnection': 1})

    def test_register_multiple_with_alias(self):
        c1 = ConnectionMock(); c2 = ConnectionMock(); c3 = ConnectionMock()
        for i, conn in enumerate([c1,c2,c3]):
            index = self.cache.register(conn, 'c%d' % (i+1))
            assert_equal(index, i+1)
            assert_equal(self.cache.current, conn)
        assert_equal(self.cache._connections, [c1, c2, c3])
        assert_equal(self.cache._aliases, {'c1': 1, 'c2': 2, 'c3': 3})

    def test_switch_with_alias(self):
        self._register('a', 'b', 'c', 'd', 'e')
        assert_equal(self.cache.current.id, 'e')
        self.cache.switch('a')
        assert_equal(self.cache.current.id, 'a')
        self.cache.switch('C')
        assert_equal(self.cache.current.id, 'c')
        self.cache.switch('  B   ')
        assert_equal(self.cache.current.id, 'b')

    def test_switch_with_non_existing_alias(self):
        self._register('a', 'b')
        assert_raises_with_msg(RuntimeError,
                               "Non-existing index or alias 'whatever'.",
                               self.cache.switch, 'whatever')

    def test_switch_with_alias_overriding_index(self):
        self._register('2', '1')
        self.cache.switch(1)
        assert_equal(self.cache.current.id, '2')
        self.cache.switch('1')
        assert_equal(self.cache.current.id, '1')

    def test_get_connection_with_index(self):
        self._register('a', 'b')
        assert_equal(self.cache.get_connection(1).id, 'a')
        assert_equal(self.cache.current.id, 'b')
        assert_equal(self.cache[2].id, 'b')

    def test_get_connection_with_alias(self):
        self._register('a', 'b')
        assert_equal(self.cache.get_connection('a').id, 'a')
        assert_equal(self.cache.current.id, 'b')
        assert_equal(self.cache['b'].id, 'b')

    def test_get_connection_with_none_returns_current(self):
        self._register('a', 'b')
        assert_equal(self.cache.get_connection().id, 'b')
        assert_equal(self.cache[None].id, 'b')

    def test_get_connection_with_none_fails_if_no_current(self):
        assert_raises_with_msg(RuntimeError,
                               'No open connection.',
                               self.cache.get_connection)

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

    def test_iter(self):
        conns = ['a', object(), 1, None]
        for c in conns:
            self.cache.register(c)
        assert_equal(list(self.cache), conns)

    def test_len(self):
        assert_equal(len(self.cache), 0)
        self.cache.register(None)
        assert_equal(len(self.cache), 1)
        self.cache.register(None)
        assert_equal(len(self.cache), 2)
        self.cache.empty_cache()
        assert_equal(len(self.cache), 0)

    def test_truthy(self):
        assert_false(self.cache)
        self.cache.register(None)
        assert_true(self.cache)
        self.cache.current_index = None
        assert_false(self.cache)
        self.cache.current_index = 1
        assert_true(self.cache)
        self.cache.empty_cache()
        assert_false(self.cache)

    def test_resolve_alias_or_index(self):
        self.cache.register(ConnectionMock(), 'alias')
        assert_equal(self.cache.resolve_alias_or_index('alias'), 1)
        assert_equal(self.cache.resolve_alias_or_index('1'), 1)
        assert_equal(self.cache.resolve_alias_or_index(1), 1)

    def test_resolve_invalid_alias_or_index(self):
        assert_raises_with_msg(ValueError,
                               "Non-existing index or alias 'nonex'.",
                               self.cache.resolve_alias_or_index, 'nonex')
        assert_raises_with_msg(ValueError,
                               "Non-existing index or alias '1'.",
                               self.cache.resolve_alias_or_index, '1')
        assert_raises_with_msg(ValueError,
                               "Non-existing index or alias '42'.",
                               self.cache.resolve_alias_or_index, 42)

    def _verify_initial_state(self):
        assert_equal(self.cache.current, self.cache._no_current)
        assert_equal(self.cache.current_index, None)
        assert_equal(self.cache._connections, [])
        assert_equal(self.cache._aliases, {})

    def _register(self, *ids):
        connections = []
        for id in ids:
            conn = ConnectionMock(id)
            self.cache.register(conn, id)
            connections.append(conn)
        return connections


if __name__ == '__main__':
    unittest.main()
