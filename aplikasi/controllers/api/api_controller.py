from aplikasi import (log, router)
from fastapi import Request, Depends, Body
from fastapi_limiter.depends import RateLimiter
from aplikasi.others.response import response_service
from aplikasi.others.utility import safe_json, validate_request_datetime
from typing import Union
import traceback

from aplikasi.controllers.api.send_notification_controller import send_notification
from aplikasi.controllers.api.send_bulk_notification_controller import send_bulk_notification
from aplikasi.controllers.api.get_notification_list_controller import get_notification_list_controller
from aplikasi.controllers.api.get_notification_detail_controller import get_notification_detail_controller
from aplikasi.controllers.api.mark_read_controller import mark_read_controller
from aplikasi.controllers.api.mark_all_read_controller import mark_all_read_controller
from aplikasi.controllers.api.get_unread_count_controller import get_unread_count_controller
from aplikasi.controllers.api.delete_notification_controller import delete_notification_controller
from aplikasi.controllers.api.register_device_token_controller import register_device_token_controller
from aplikasi.controllers.api.get_notification_summary_controller import get_notification_summary_controller

from aplikasi.models.api_model import (
    SendNotificationRequest,
    SendBulkNotificationRequest,
    GetNotificationListRequest,
    GetNotificationDetailRequest,
    MarkReadRequest,
    MarkAllReadRequest,
    GetUnreadCountRequest,
    DeleteNotificationRequest,
    RegisterDeviceTokenRequest,
    GetNotificationSummaryRequest,
)

InquiryRequestUnion = Union[
    SendNotificationRequest,
    SendBulkNotificationRequest,
    GetNotificationListRequest,
    GetNotificationDetailRequest,
    MarkReadRequest,
    MarkAllReadRequest,
    GetUnreadCountRequest,
    DeleteNotificationRequest,
    RegisterDeviceTokenRequest,
    GetNotificationSummaryRequest,
]


@router.post("/inquiry-docs", response_model=None, summary="Dokumentasi Skema /inquiry", tags=["Inquiry"])
async def inquiry_docs(body: InquiryRequestUnion = Body(...)):
    return {"message": "Hanya untuk dokumentasi schema"}


@router.post("/inquiry", dependencies=[Depends(RateLimiter(times=50, seconds=60))], include_in_schema=False)
async def inquiry(request: Request):
    try:
        data_request    = await safe_json(request)
        v_method        = data_request.get("method", "")
        v_datetime      = data_request.get("datetime", "")

        v_is_valid, v_msg = validate_request_datetime(v_datetime)
        if not v_is_valid:
            return await response_service(request, v_method, 405, 405, v_msg)

        if v_method == "send_notification":
            return await send_notification(request)
        elif v_method == "send_bulk_notification":
            return await send_bulk_notification(request)
        elif v_method == "get_notification_list":
            return await get_notification_list_controller(request)
        elif v_method == "get_notification_detail":
            return await get_notification_detail_controller(request)
        elif v_method == "mark_read":
            return await mark_read_controller(request)
        elif v_method == "mark_all_read":
            return await mark_all_read_controller(request)
        elif v_method == "get_unread_count":
            return await get_unread_count_controller(request)
        elif v_method == "delete_notification":
            return await delete_notification_controller(request)
        elif v_method == "register_device_token":
            return await register_device_token_controller(request)
        elif v_method == "get_notification_summary":
            return await get_notification_summary_controller(request)
        else:
            return await response_service(request, v_method, 405, 405, "Invalid Method")

    except Exception as e:
        log.error(f"===== ERROR INQUIRY ===== : {e}")
        traceback.print_exc()
        return await response_service(request, v_method, 405, 401, "Internal Server Error")


@router.get("/health", include_in_schema=False)
async def health():
    return {"status": "running"}


@router.get("/")
async def root():
    return {"status": "running"}
