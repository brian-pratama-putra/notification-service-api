from typing import Optional, List
from pydantic import BaseModel

inquiry_examples = {
    "send_notification": {
        "summary": "Kirim notifikasi ke satu user",
        "value": {
            "method": "send_notification",
            "target_user_id": "uuid-user-target",
            "channel": "in_app",
            "title": "Pesanan Dikonfirmasi",
            "body": "Pesanan #ORD001 kamu sudah dikonfirmasi.",
            "data": {"order_id": "ORD001", "action": "open_order"},
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "abc123"
        }
    },
    "send_bulk_notification": {
        "summary": "Kirim notifikasi ke banyak user sekaligus",
        "value": {
            "method": "send_bulk_notification",
            "target_user_ids": ["uuid-user-1", "uuid-user-2", "uuid-user-3"],
            "channel": "in_app",
            "title": "Promo Spesial!",
            "body": "Dapatkan diskon 50% hari ini saja.",
            "data": {"promo_id": "PROMO001"},
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "abc456"
        }
    },
    "get_notification_list": {
        "summary": "Daftar notifikasi milik user",
        "value": {
            "method": "get_notification_list",
            "is_read": "false",
            "channel": "in_app",
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "abc789"
        }
    },
    "get_notification_detail": {
        "summary": "Detail satu notifikasi",
        "value": {
            "method": "get_notification_detail",
            "notification_id": "uuid-notif",
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "def123"
        }
    },
    "mark_read": {
        "summary": "Tandai notifikasi sudah dibaca",
        "value": {
            "method": "mark_read",
            "notification_id": "uuid-notif",
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "def456"
        }
    },
    "mark_all_read": {
        "summary": "Tandai semua notifikasi sudah dibaca",
        "value": {
            "method": "mark_all_read",
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "ghi123"
        }
    },
    "get_unread_count": {
        "summary": "Jumlah notifikasi belum dibaca",
        "value": {
            "method": "get_unread_count",
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "ghi456"
        }
    },
    "delete_notification": {
        "summary": "Hapus notifikasi",
        "value": {
            "method": "delete_notification",
            "notification_id": "uuid-notif",
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "jkl123"
        }
    },
    "register_device_token": {
        "summary": "Daftarkan device token untuk push notification",
        "value": {
            "method": "register_device_token",
            "device_token": "fcm-token-xxx",
            "platform": "android",
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "jkl456"
        }
    },
    "get_notification_summary": {
        "summary": "Ringkasan notifikasi user",
        "value": {
            "method": "get_notification_summary",
            "session_key": "sess_xxx",
            "datetime": "2025-07-29 12:00:00",
            "checksum": "mno123"
        }
    },
}


class SendNotificationRequest(BaseModel):
    method: str
    target_user_id: str
    channel: str
    title: str
    body: str
    data: Optional[dict] = None
    session_key: str
    datetime: str
    checksum: str


class SendBulkNotificationRequest(BaseModel):
    method: str
    target_user_ids: List[str]
    channel: str
    title: str
    body: str
    data: Optional[dict] = None
    session_key: str
    datetime: str
    checksum: str


class GetNotificationListRequest(BaseModel):
    method: str
    is_read: Optional[str] = None
    channel: Optional[str] = None
    session_key: str
    datetime: str
    checksum: str


class GetNotificationDetailRequest(BaseModel):
    method: str
    notification_id: str
    session_key: str
    datetime: str
    checksum: str


class MarkReadRequest(BaseModel):
    method: str
    notification_id: str
    session_key: str
    datetime: str
    checksum: str


class MarkAllReadRequest(BaseModel):
    method: str
    session_key: str
    datetime: str
    checksum: str


class GetUnreadCountRequest(BaseModel):
    method: str
    session_key: str
    datetime: str
    checksum: str


class DeleteNotificationRequest(BaseModel):
    method: str
    notification_id: str
    session_key: str
    datetime: str
    checksum: str


class RegisterDeviceTokenRequest(BaseModel):
    method: str
    device_token: str
    platform: str
    session_key: str
    datetime: str
    checksum: str


class GetNotificationSummaryRequest(BaseModel):
    method: str
    session_key: str
    datetime: str
    checksum: str
