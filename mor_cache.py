
import threading
import time


class MorNotFoundError(Exception):
    pass


class MorCache:
    """
    Implements a thread safe storage for Mor objects.
    """
    def __init__(self):
        self._mor = {}
        self._mor_lock = threading.RLock()

    def init_instance(self, key):
        with self._mor_lock:
            if key not in self._mor:
                self._mor[key] = {}

    def contains(self, key):
        with self._mor_lock:
            return key in self._mor

    def instance_size(self, key):
        """
        Return how many Mor objects are stored for the given instance.
        """
        with self._mor_lock:
            return len(self._mor[key])

    def set_mor(self, key, name, mor):
        """
        Store a Mor object in the cache with the given name.
        """
        with self._mor_lock:
            self._mor[key][name] = mor
            self._mor[key][name]['creation_time'] = time.time()

    def get_mor(self, key, name):
        """
        Return the Mor object identified by `name` for the given instance key.
        """
        with self._mor_lock:
            mors = self._mor[key]
            try:
                return mors[name]
            except KeyError:
                raise MorNotFoundError("Mor object '{}' is not in the cache.".format(name))

    def set_metrics(self, key, name, metrics):
        """
        Store a list of metric identifiers for the given instance key and Mor
        object name.
        """
        with self._mor_lock:
            mor = self._mor[key].get(name)
            if mor is None:
                raise MorNotFoundError("Mor object '{}' is not in the cache.".format(name))
            mor['metrics'] = metrics

    def mors(self, key):
        """
        Generator returning all the mors in the cache for the given instance key.
        """
        with self._mor_lock:
            for k, v in self._mor.get(key, {}).items():
                yield k, v

    def mors_batch(self, key, batch_size):
        """
        Generator returning as many dictionaries containing `batch_size` Mor
        objects as needed to iterate all the content of the cache.
        """
        with self._mor_lock:
            mors_dict = self._mor.get(key)
            if mors_dict is None:
                yield {}

            mor_names = mors_dict.keys()
            mor_names = sorted(mor_names)
            total = len(mor_names)
            for idx in range(0, total, batch_size):
                names_chunk = mor_names[idx:min(idx + batch_size, total)]
                yield {name: mors_dict[name] for name in names_chunk}

    def purge(self, key, ttl):
        """
        Remove all the items in the cache for the given key that are older than
        ttl seconds.
        """
        mors_to_purge = []
        now = time.time()
        with self._mor_lock:
            # Don't change the dict during iteration!
            # First collect the names of the Mors to remove...
            for name, mor in self._mor[key].items():
                age = now - mor['creation_time']
                if age > ttl:
                    mors_to_purge.append(name)

            # ...then actually remove the Mors from the cache.
            for name in mors_to_purge:
                del self._mor[key][name]
