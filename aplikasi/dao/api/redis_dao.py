import json
from aplikasi.dao.query_file import connection_redis_async


async def cache_get(p_key: str):
    try:
        v_redis_client  = await connection_redis_async()
        v_result        = await v_redis_client.get(p_key)
        return json.loads(v_result) if v_result else None
    except Exception as e:
        print(f"Redis get error for key {p_key}: {e}")
        return None


async def cache_set(p_key: str, p_value, ttl: int = 86400):
    try:
        v_redis_client = await connection_redis_async()
        await v_redis_client.setex(p_key, ttl, json.dumps(p_value))
    except Exception as e:
        print(f"Redis set error for key {p_key}: {e}")


async def cache_delete(p_key: str):
    try:
        v_redis_client = await connection_redis_async()
        await v_redis_client.delete(p_key)
    except Exception as e:
        print(f"Redis delete error for key {p_key}: {e}")


async def cache_incr(p_key: str, ttl: int = None):
    try:
        v_redis_client  = await connection_redis_async()
        v_result        = await v_redis_client.incr(p_key)
        if ttl and v_result == 1:
            await v_redis_client.expire(p_key, ttl)
        return v_result
    except Exception as e:
        print(f"Redis incr error for key {p_key}: {e}")
        return None


async def cache_decr(p_key: str):
    try:
        v_redis_client = await connection_redis_async()
        return await v_redis_client.decr(p_key)
    except Exception as e:
        print(f"Redis decr error for key {p_key}: {e}")
        return None
