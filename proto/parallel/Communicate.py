from Queue import Queue
from threading import Event
try:
    from multiprocessing.managers import BaseManager
except ImportError:
    class Python26Required(object):
          def __call__(self, *args):
            raise RuntimeError('Requires Python > 2.6')
          def __getattr__(self, name):
            raise RuntimeError('Requires Python > 2.6')
    BaseManager = Python26Required()

class _create_caching_getter(object):

    def __init__(self, clazz):
        self._clazz = clazz
        self._objects = {}

    def __call__(self, key):
        if key not in self._objects:
            self._objects[key] = self._clazz()
        return self._objects[key]

class Communicate(object):
    """Library for communication between processes.
    For example this can be used to handle communication between processes of the Parallel robot library.
    
    Requires Python 2.6
    
    Example:
    
    Process 1 test file:
    | *Settings* |
    | Library | Communicate |
    
    
    | *Test Cases* |
    | Communicator |
    |        | [Setup] | Start Communication Service |
    |        | Send Message To | my message queue     | hello world!        |
    |        | ${message}=     | Receive Message From | other message queue |
    |        | Should Be Equal | ${message}           | hello!              |
    |        | [Teardown] | Stop Communication Service |
    
    Process 2 test file:
    | *Settings* |
    | Library | Communicate | ${process 1 ip address if on a different machine} |
    
    
    | *Test Cases* |
    | Helloer |
    |         | ${message}= | Receive Message From | my message queue |
    |         | Should Be Equal | ${message}          | hello world!  |
    |         | Send Message To | other message queue | hello!        |
    
    """

    def __init__(self, address='127.0.0.1', port=2187):
        """
        `address` of the communication server.
        `port` of the communication server.
        """
        self._address = address
        self._port = int(port)
        self._authkey = 'live long and prosper'
        self._queue = None
        self._connected = False

    def _connect(self):
        self._create_manager().connect()
        self._connected = True

    def start_communication_service(self):
        """Starts a communication server that will be used to share messages and objects between processes.
        """
        self._create_manager(_create_caching_getter(Queue),
                             _create_caching_getter(Event)).start()
        self._connected = True

    def stop_communication_service(self):
        """Stops a started communication server. 
        This ensures that the server and the messages that it has don't influence the next tests.
        To ensure that this keyword really happens place this in the teardown section.
        """
        self._manager.shutdown()
        self._connected = False

    def _create_manager(self, queue_getter=None, event_getter=None):
        BaseManager.register('get_queue', queue_getter)
        BaseManager.register('get_event', event_getter)
        self._manager = BaseManager((self._address, self._port), self._authkey)
        return self._manager

    def send_message_to(self, queue_id, value):
        """Send a message to a message queue.

        `queue_id` is the identifier for the queue.

        `value` is the message. This can be a string, a number or any serializable object.

        Example:
        In one process
        | Send Message To | my queue | hello world! |
        ...
        In another process
        | ${message}= | Receive Message From | my queue |
        | Should Be Equal | ${message} | hello world! |
        """
        self._get_queue(queue_id).put(value)

    def receive_message_from(self, queue_id, timeout=None):
        """Receive and consume a message from a message queue.
        By default this keyword will block until there is a message in the queue.

        `queue_id` is the identifier for the queue.

        `timeout` is the time out in seconds to wait.

        Returns the value from the message queue. Fails if timeout expires.

        Example:
        In one process
        | Send Message To | my queue | hello world! |
        ...
        In another process
        | ${message}= | Receive Message From | my queue |
        | Should Be Equal | ${message} | hello world! |
        """
        timeout = float(timeout) if timeout is not None else None
        return self._get_queue(queue_id).get(timeout=timeout)

    def _get_queue(self, queue_id):
        if not self._connected:
            self._connect()
        return self._manager.get_queue(queue_id)

    def wait_for_event(self, event_id):
        """Waits until event with `event_id` is signaled.

        Example:
        In one process
        | Wait For Event | my event |
        ...
        In another process
        | Signal Event | my event |
        """
        return self._get_event(event_id).wait()

    def signal_event(self, event_id):
        """Signals an event.
        If a process is waiting for this event it will stop waiting after the signal.

        `event` is the identifier for the event.

        Example:
        In one process
        | Wait For Event | my event |
        ...
        In another process
        | Signal Event | my event |
        """
        return self._get_event(event_id).set()

    def _get_event(self, event_id):
        if not self._connected:
            self._connect()
        return self._manager.get_event(event_id)

