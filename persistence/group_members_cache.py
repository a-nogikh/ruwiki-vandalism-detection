import operator
import redis
import cachetools


class GroupMembersCache:
    # We store two keys: one is for the data, the other one is important in the (rare)
    # case when there are no users of the group.
    # We need to differentiate two cases:
    # 1) when the set has aged out and therefore it is empty
    # 2) when the set is intentionally empty
    
    KEY_SET_PREFIX="group-members-"
    KEY_LOADED_FLAG_PREFIX="group-members-loaded"

    def __init__(self, redis_client: redis.StrictRedis):
        self.redis = redis_client
        self.func_cache = cachetools.TTLCache(maxsize=16, ttl=30)

    # returns None if the required set does not exist
    @cachetools.cachedmethod(operator.attrgetter('func_cache'))
    def load_set(self, group_name) -> set:
        loaded_flag = self.redis.get(self.KEY_LOADED_FLAG_PREFIX + group_name)
        if not loaded_flag:
            return None

        set_generator = self.redis.smembers(self.KEY_SET_PREFIX + group_name)
        return set(int(x) for x in set_generator)

    def save_set(self, group_name, group_members: set, expire_seconds: int):
        key = GroupMembersCache.KEY_SET_PREFIX + group_name
        self.redis.delete(key)
        self.redis.sadd(key, *group_members)
        self.redis.expire(key, expire_seconds)

        key_flag = GroupMembersCache.KEY_LOADED_FLAG_PREFIX + group_name
        self.redis.set(key_flag, 1)
        self.redis.expire(key_flag, expire_seconds)
        
        self.func_cache.clear()
