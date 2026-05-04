from aplikasi import (log, secret_key_request)
from aplikasi.others.response import response_service
from aplikasi.others.format import generate_checksum
from aplikasi.dao.api.db_dao import get_unread_count_db
from aplikasi.dao.api.redis_dao import cache_get
import asyncio


async def get_unread_count_controller(request):
    data = await request.json()

    v_method        = data.get("method", "")
    v_session_key   = data.get("session_key", "")
    v_datetime      = data.get("datetime", "")
    v_checksum      = data.get("checksum", "")

    if not all([v_session_key, v_datetime, v_checksum]):
        return await response_service(request, v_method, 422, 400, "Invalid Request Data")

    v_app_payload   = f"{v_method}#{v_datetime}#{secret_key_request}"
    v_app_checksum  = generate_checksum(v_app_payload)

    if v_checksum != v_app_checksum:
        return await response_service(request, v_method, 406, 401, "Invalid Key")

    v_session_data = await cache_get(f"session_key:{v_session_key}")
    if not v_session_data:
        return await response_service(request, v_method, 401, 401, "Session tidak valid atau sudah expired")

    v_user_id = v_session_data.get("user_id", "")

    v_redis_client  = await __import__("aplikasi.dao.query_file", fromlist=["connection_redis_async"]).connection_redis_async()
    v_cached_count  = await v_redis_client.get(f"notif:unread:{v_user_id}")

    if v_cached_count is not None:
        return await response_service(request, v_method, 200, 200, "Success", {
            "unread_count": v_cached_count
        })

    v_hasil = await asyncio.to_thread(get_unread_count_db, v_user_id)

    if v_hasil["status"] == "T" and v_hasil["result"]:
        v_count = v_hasil["result"][0]["unread_count"]
        return await response_service(request, v_method, 200, 200, "Success", {
            "unread_count": v_count
        })
    else:
        return await response_service(request, v_method, 400, 400, v_hasil["message"])
