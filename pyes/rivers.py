class River(object):
    def __init__(self, index_name=None, index_type=None, bulk_size=100, bulk_timeout=None):
        self.name = index_name
        self.index_name = index_name
        self.index_type = index_type
        self.bulk_size = bulk_size
        self.bulk_timeout = bulk_timeout

    @property
    def q(self):
        res = self.serialize()
        index = {}
        if self.name:
            index['name'] = self.name
        if self.index_name:
            index['index'] = self.index_name
        if self.index_type:
            index['type'] = self.index_type
        if self.bulk_size:
            index['bulk_size'] = self.bulk_size
        if self.bulk_timeout:
            index['bulk_timeout'] = self.bulk_timeout
        if index:
            res['index'] = index
        return res

    def __repr__(self):
        return str(self.q)

    def serialize(self):
        raise NotImplementedError


class RabbitMQRiver(River):
    type = "rabbitmq"

    def __init__(self, host="localhost", port=5672, user="guest",
                 password="guest", vhost="/", queue="es", exchange="es",
                 routing_key="es", **kwargs):
        super(RabbitMQRiver, self).__init__(**kwargs)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key

    def serialize(self):
        return {
            "type": self.type,
            self.type: {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "pass": self.password,
                "vhost": self.vhost,
                "queue": self.queue,
                "exchange": self.exchange,
                "routing_key": self.routing_key
            }
        }


class TwitterRiver(River):
    type = "twitter"

    def __init__(self, user=None, password=None, **kwargs):
        self.user = user
        self.password = password
        self.consumer_key = kwargs.pop('consumer_key', None)
        self.consumer_secret = kwargs.pop('consumer_secret', None)
        self.access_token = kwargs.pop('access_token', None)
        self.access_token_secret = kwargs.pop('access_token_secret', None)
        # These filters may be lists or comma-separated strings of values
        self.tracks = kwargs.pop('tracks', None)
        self.follow = kwargs.pop('follow', None)
        self.locations = kwargs.pop('locations', None)
        super(TwitterRiver, self).__init__(**kwargs)

    def serialize(self):
        result = {"type": self.type}
        if self.user and self.password:
            result[self.type] = {"user": self.user,
                       "password": self.password}
        elif (self.consumer_key and self.consumer_secret and self.access_token
              and self.access_token_secret):
            result[self.type] = {"oauth": {
                "consumer_key": self.consumer_key,
                "consumer_secret": self.consumer_secret,
                "access_token": self.access_token,
                "access_token_secret": self.access_token_secret,
            }
            }
        else:
            raise ValueError("Twitter river requires authentication by username/password or OAuth")
        filter = {}
        if self.tracks:
            filter['tracks'] = self.tracks
        if self.follow:
            filter['follow'] = self.follow
        if self.locations:
            filter['locations'] = self.locations
        if filter:
            result[self.type]['filter'] = filter
        return result

class CouchDBRiver(River):
    type = "couchdb"

    def __init__(self, host="localhost", port=5984, db="mydb", filter=None,
                 filter_params=None, script=None, user=None, password=None,
                 **kwargs):
        super(CouchDBRiver, self).__init__(**kwargs)
        self.host = host
        self.port = port
        self.db = db
        self.filter = filter
        self.filter_params = filter_params
        self.script = script
        self.user = user
        self.password = password

    def serialize(self):
        result = {
            "type": self.type,
            self.type: {
                "host": self.host,
                "port": self.port,
                "db": self.db,
                "filter": self.filter,
                }
        }
        if self.filter_params is not None:
            result[self.type]["filter_params"] = self.filter_params
        if self.script is not None:
            result[self.type]["script"] = self.script
        if self.user is not None:
            result[self.type]["user"] = self.user
        if self.password is not None:
            result[self.type]["password"] = self.password
        return result
