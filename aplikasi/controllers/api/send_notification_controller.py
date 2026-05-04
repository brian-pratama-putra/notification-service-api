from aplikasi import (log, secret_key_request, settings)
from aplikasi.others.response import response_service
from aplikasi.others.format import generate_checksum
from aplikasi.dao.api.db_dao import insert_notification
from aplikasi.dao.api.redis_dao import cache_get, cache_delete, cache_incr
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


async def send_email_async(p_to_email, p_title, p_body):
    try:
        v_msg               = MIMEMultipart()
        v_msg["From"]       = settings.SMTP_FROM
        v_msg["To"]         = p_to_email
        v_msg["Subject"]    = p_title
        v_msg.attach(MIMEText(p_body, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as v_server:
            v_server.starttls()
            v_server.login(settings.SMTP_USER, settings.SMTP_PASS)
            v_server.sendmail(settings.SMTP_FROM, p_to_email, v_msg.as_string())
    except Exception as e:
        log.error(f"Failed send email to {p_to_email}: {e}")


async def send_notification(request):
    data = await request.json()

    v_method            = data.get("method", "")
    v_target_user_id    = data.get("target_user_id", "")
    v_channel           = data.get("channel", "")
    v_title             = data.get("title", "")
    v_body              = data.get("body", "")
    v_data              = data.get("data", None)
    v_session_key       = data.get("session_key", "")
    v_datetime          = data.get("datetime", "")
    v_checksum          = data.get("checksum", "")

    if not all([v_target_user_id, v_channel, v_title, v_body, v_session_key, v_datetime, v_checksum]):
        return await response_service(request, v_method, 422, 400, "Invalid Request Data")

    if v_channel not in ("in_app", "email", "push"):
        return await response_service(request, v_method, 422, 400, "Channel harus in_app, email, atau push")

    v_app_payload   = f"{v_method}#{v_target_user_id}#{v_channel}#{v_datetime}#{secret_key_request}"
    v_app_checksum  = generate_checksum(v_app_payload)

    if v_checksum != v_app_checksum:
        return await response_service(request, v_method, 406, 401, "Invalid Key")

    v_session_data = await cache_get(f"session_key:{v_session_key}")
    if not v_session_data:
        return await response_service(request, v_method, 401, 401, "Session tidak valid atau sudah expired")

    v_hasil = await asyncio.to_thread(insert_notification, v_target_user_id, v_channel, v_title, v_body, v_data)

    if v_hasil["status"] == "T" and v_hasil["result"]:
        v_notification_id = str(v_hasil["result"][0]["notification_id"])

        await cache_delete(f"notif:list:{v_target_user_id}:all:all")
        await cache_delete(f"notif:summary:{v_target_user_id}")
        await cache_incr(f"notif:unread:{v_target_user_id}", ttl=86400)

        if v_channel == "email":
            v_user_data = await cache_get(f"user:profile:{v_target_user_id}")
            if v_user_data and v_user_data.get("email"):
                asyncio.create_task(send_email_async(v_user_data["email"], v_title, v_body))

        return await response_service(request, v_method, 200, 200, "Success", {
            "notification_id": v_notification_id
        })
    else:
        return await response_service(request, v_method, 400, 400, v_hasil["message"])
