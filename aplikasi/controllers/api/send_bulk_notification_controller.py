import json
from aplikasi import (log, secret_key_request)
from aplikasi.others.response import response_service
from aplikasi.others.format import generate_checksum
from aplikasi.dao.api.db_dao import insert_bulk_notification
from aplikasi.dao.api.redis_dao import cache_get, cache_delete, cache_incr
import asyncio


async def send_bulk_notification(request):
    data = await request.json()

    v_method            = data.get("method", "")
    v_target_user_ids   = data.get("target_user_ids", [])
    v_channel           = data.get("channel", "")
    v_title             = data.get("title", "")
    v_body              = data.get("body", "")
    v_data              = data.get("data", None)
    v_session_key       = data.get("session_key", "")
    v_datetime          = data.get("datetime", "")
    v_checksum          = data.get("checksum", "")

    if not all([v_target_user_ids, v_channel, v_title, v_body, v_session_key, v_datetime, v_checksum]):
        return await response_service(request, v_method, 422, 400, "Invalid Request Data")

    if not isinstance(v_target_user_ids, list) or len(v_target_user_ids) == 0:
        return await response_service(request, v_method, 422, 400, "target_user_ids harus berupa list dan tidak boleh kosong")

    if len(v_target_user_ids) > 1000:
        return await response_service(request, v_method, 422, 400, "Maksimal 1000 user per bulk notification")

    if v_channel not in ("in_app", "email", "push"):
        return await response_service(request, v_method, 422, 400, "Channel harus in_app, email, atau push")

    v_app_payload   = f"{v_method}#{v_channel}#{v_title}#{v_datetime}#{secret_key_request}"
    v_app_checksum  = generate_checksum(v_app_payload)

    if v_checksum != v_app_checksum:
        return await response_service(request, v_method, 406, 401, "Invalid Key")

    v_session_data = await cache_get(f"session_key:{v_session_key}")
    if not v_session_data:
        return await response_service(request, v_method, 401, 401, "Session tidak valid atau sudah expired")

    v_rows = [
        {
            "user_id" : uid,
            "channel" : v_channel,
            "title"   : v_title,
            "body"    : v_body,
            "data"    : json.dumps(v_data) if v_data else None,
        }
        for uid in v_target_user_ids
    ]

    v_hasil = await asyncio.to_thread(insert_bulk_notification, v_rows)

    if v_hasil["status"] == "T":
        for v_uid in v_target_user_ids:
            await cache_delete(f"notif:list:{v_uid}:all:all")
            await cache_delete(f"notif:summary:{v_uid}")
            await cache_incr(f"notif:unread:{v_uid}", ttl=86400)

        return await response_service(request, v_method, 200, 200, "Success", {
            "total_sent": str(len(v_target_user_ids))
        })
    else:
        return await response_service(request, v_method, 400, 400, v_hasil["message"])
