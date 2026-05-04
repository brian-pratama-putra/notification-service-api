import json
from aplikasi.dao.query_file import CreateConnectionDb, QueryStringDb, response_json
from aplikasi.dao.api.redis_dao import cache_get, cache_set, cache_delete, cache_incr, cache_decr


def insert_notification(p_user_id, p_channel, p_title, p_body, p_data):
    try:
        with CreateConnectionDb({"read": False, "write": True}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_query             = """
                                    INSERT INTO notifications
                                    (user_id, channel, title, body, data, created_at)
                                    VALUES(%(user_id)s, %(channel)s, %(title)s, %(body)s, %(data)s,
                                    CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Jakarta')
                                    RETURNING notification_id
                                """
            v_kondisi           = {
                                    "user_id" : p_user_id,
                                    "channel" : p_channel,
                                    "title"   : p_title,
                                    "body"    : p_body,
                                    "data"    : json.dumps(p_data) if p_data else None,
                                }
            return v_query_string_db.select(v_query, v_kondisi)
    except Exception as e:
        return response_json(400, "F", str(e), [])


def insert_bulk_notification(p_rows: list):
    try:
        with CreateConnectionDb({"read": False, "write": True}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_query             = """
                                    INSERT INTO notifications
                                    (user_id, channel, title, body, data, created_at)
                                    VALUES(%(user_id)s, %(channel)s, %(title)s, %(body)s, %(data)s,
                                    CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Jakarta')
                                """
            return v_query_string_db.execute_many(v_query, p_rows)
    except Exception as e:
        return response_json(400, "F", str(e), None)


async def get_notification_list(p_user_id, p_is_read=None, p_channel=None):
    v_cache_key     = f"notif:list:{p_user_id}:{p_is_read or 'all'}:{p_channel or 'all'}"
    cached_result   = await cache_get(v_cache_key)
    if cached_result:
        return response_json(200, "T", "Success", cached_result)

    try:
        with CreateConnectionDb({"read": True, "write": False}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_kondisi           = {"user_id": p_user_id}
            v_where_extra       = ""

            if p_is_read is not None:
                v_where_extra           += " AND is_read = %(is_read)s"
                v_kondisi["is_read"]    = p_is_read == "true"
            if p_channel:
                v_where_extra           += " AND channel = %(channel)s"
                v_kondisi["channel"]    = p_channel

            v_query = f"""
                        SELECT
                            notification_id::varchar,
                            channel,
                            title,
                            body,
                            is_read,
                            to_char(read_at, 'YYYY-MM-DD HH24:MI:SS') read_at,
                            to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') created_at
                        FROM notifications
                        WHERE user_id = %(user_id)s
                        AND is_deleted = false
                        {v_where_extra}
                        ORDER BY created_at DESC
                        LIMIT 100
                    """
            v_hasil = v_query_string_db.select(v_query, v_kondisi)
            if v_hasil["status"] == "T" and v_hasil["result"]:
                await cache_set(v_cache_key, v_hasil["result"], ttl=60)
            return v_hasil
    except Exception as e:
        return response_json(400, "F", str(e), [])


def get_notification_detail(p_notification_id, p_user_id):
    try:
        with CreateConnectionDb({"read": True, "write": False}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_query             = """
                                    SELECT
                                        notification_id::varchar,
                                        channel,
                                        title,
                                        body,
                                        coalesce(data::text, '{}') data,
                                        is_read,
                                        to_char(read_at, 'YYYY-MM-DD HH24:MI:SS') read_at,
                                        to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') created_at
                                    FROM notifications
                                    WHERE notification_id = %(notification_id)s
                                    AND user_id = %(user_id)s
                                    AND is_deleted = false
                                """
            v_kondisi           = {
                                    "notification_id" : p_notification_id,
                                    "user_id"         : p_user_id,
                                }
            return v_query_string_db.select(v_query, v_kondisi)
    except Exception as e:
        return response_json(400, "F", str(e), [])


def mark_notification_read(p_notification_id, p_user_id):
    try:
        with CreateConnectionDb({"read": False, "write": True}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_query             = """
                                    UPDATE notifications
                                    SET is_read = true,
                                    read_at = CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Jakarta'
                                    WHERE notification_id = %(notification_id)s
                                    AND user_id = %(user_id)s
                                    AND is_read = false
                                    AND is_deleted = false
                                """
            v_kondisi           = {
                                    "notification_id" : p_notification_id,
                                    "user_id"         : p_user_id,
                                }
            return v_query_string_db.execute(v_query, v_kondisi)
    except Exception as e:
        return response_json(400, "F", str(e), None)


def mark_all_notifications_read(p_user_id):
    try:
        with CreateConnectionDb({"read": False, "write": True}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_query             = """
                                    UPDATE notifications
                                    SET is_read = true,
                                    read_at = CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Jakarta'
                                    WHERE user_id = %(user_id)s
                                    AND is_read = false
                                    AND is_deleted = false
                                """
            v_kondisi           = {"user_id": p_user_id}
            return v_query_string_db.execute(v_query, v_kondisi)
    except Exception as e:
        return response_json(400, "F", str(e), None)


def get_unread_count_db(p_user_id):
    try:
        with CreateConnectionDb({"read": True, "write": False}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_query             = """
                                    SELECT COUNT(*)::varchar unread_count
                                    FROM notifications
                                    WHERE user_id = %(user_id)s
                                    AND is_read = false
                                    AND is_deleted = false
                                """
            v_kondisi           = {"user_id": p_user_id}
            return v_query_string_db.select(v_query, v_kondisi)
    except Exception as e:
        return response_json(400, "F", str(e), [])


def delete_notification(p_notification_id, p_user_id):
    try:
        with CreateConnectionDb({"read": False, "write": True}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_query             = """
                                    UPDATE notifications
                                    SET is_deleted = true
                                    WHERE notification_id = %(notification_id)s
                                    AND user_id = %(user_id)s
                                    AND is_deleted = false
                                """
            v_kondisi           = {
                                    "notification_id" : p_notification_id,
                                    "user_id"         : p_user_id,
                                }
            return v_query_string_db.execute(v_query, v_kondisi)
    except Exception as e:
        return response_json(400, "F", str(e), None)


def upsert_device_token(p_user_id, p_device_token, p_platform):
    try:
        with CreateConnectionDb({"read": False, "write": True}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_query             = """
                                    INSERT INTO device_tokens (user_id, device_token, platform, updated_at)
                                    VALUES(%(user_id)s, %(device_token)s, %(platform)s,
                                    CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Jakarta')
                                    ON CONFLICT (user_id, platform)
                                    DO UPDATE SET
                                        device_token = %(device_token)s,
                                        updated_at = CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Jakarta'
                                """
            v_kondisi           = {
                                    "user_id"       : p_user_id,
                                    "device_token"  : p_device_token,
                                    "platform"      : p_platform,
                                }
            return v_query_string_db.execute(v_query, v_kondisi)
    except Exception as e:
        return response_json(400, "F", str(e), None)


async def get_notification_summary(p_user_id):
    v_cache_key     = f"notif:summary:{p_user_id}"
    cached_result   = await cache_get(v_cache_key)
    if cached_result:
        return response_json(200, "T", "Success", cached_result)

    try:
        with CreateConnectionDb({"read": True, "write": False}) as v_connection_db:
            v_query_string_db   = QueryStringDb(v_connection_db)
            v_query             = """
                                    SELECT
                                        COUNT(*)::varchar                                                               total_notification,
                                        COUNT(CASE WHEN is_read = false THEN 1 END)::varchar                           total_unread,
                                        COUNT(CASE WHEN channel = 'in_app' THEN 1 END)::varchar                        total_in_app,
                                        COUNT(CASE WHEN channel = 'email' THEN 1 END)::varchar                         total_email,
                                        COUNT(CASE WHEN channel = 'push' THEN 1 END)::varchar                          total_push,
                                        COUNT(CASE WHEN created_at::date = CURRENT_DATE THEN 1 END)::varchar            total_today
                                    FROM notifications
                                    WHERE user_id = %(user_id)s
                                    AND is_deleted = false
                                """
            v_kondisi           = {"user_id": p_user_id}
            v_hasil             = v_query_string_db.select(v_query, v_kondisi)
            if v_hasil["status"] == "T" and v_hasil["result"]:
                await cache_set(v_cache_key, v_hasil["result"][0], ttl=60)
            return v_hasil
    except Exception as e:
        return response_json(400, "F", str(e), [])
