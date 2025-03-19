from typing import Any

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.db.db import get_db_connection
from app.db.user import create_user, get_user_by_phone, update_user
from app.db.user_features import add_user_features, get_user_features, remove_user_features
from app.models.flows import FlowRequest
from app.utils.country_data import get_country_by_code, get_country_features
from app.utils.encryption import decrypt_request, encrypt_response
from app.utils.logging import logger

router = APIRouter()


@router.post("/flows", response_class=PlainTextResponse)
async def whatsapp_flows(data: FlowRequest):
    flow_data, aes_key, iv = decrypt_request(data.encrypted_flow_data, data.encrypted_aes_key, data.initial_vector)
    logger.info(f"Flow data {flow_data}")

    match flow_data.action:
        case "ping":
            response = {"data": {"status": "active"}}
            return encrypt_response(response, aes_key, iv)
        case "data_exchange" | "INIT" | "BACK":
            flow_token = flow_data.flow_token
            country_code, cellphone, _ = flow_token.split(":")
            async with get_db_connection() as conn:
                user = await get_user_by_phone(conn, country_code, cellphone)

            response = {}
            if flow_data.action == "INIT":
                country = get_country_by_code(country_code)
                features = get_country_features(country)
                response: dict[str, Any] = {
                    "screen": "USER_INFO",
                    "data": {
                        "features": features,
                    },
                }
                logger.info(f"Features {features}, user {user}")
                if user:
                    user_features = [user_feature.type for user_feature in await get_user_features(conn, user.id)]
                    response["data"]["init_values"] = {
                        "name": user.name,
                        "email": user.email,
                        "features": user_features,
                    }
            elif flow_data.action == "data_exchange":
                new_feature_set = set(flow_data.data.get("features", []))
                if user:
                    current_features = set(
                        [user_feature.type for user_feature in await get_user_features(conn, user.id)]
                    )
                    to_add = new_feature_set - current_features
                    to_remove = current_features - new_feature_set
                    if to_add:
                        await add_user_features(conn, user.id, to_add)
                    if to_remove:
                        await remove_user_features(conn, user.id, to_remove)
                    if user.name != flow_data.data["name"] or user.email != flow_data.data["email"]:
                        await update_user(conn, user.id, flow_data.data["name"], flow_data.data["email"])
                    await conn.commit()
                else:
                    user = await create_user(
                        conn, country_code, cellphone, flow_data.data["name"], flow_data.data["email"]
                    )
                    await add_user_features(conn, user.id, new_feature_set)
                    await conn.commit()

                response = {
                    "screen": "SUCCESS",
                    "data": {
                        "extension_message_response": {
                            "params": {
                                "flow_token": flow_token,
                                "name": flow_data.data["name"],
                                "email": flow_data.data["email"],
                                "features": flow_data.data.get("features", []),
                            }
                        }
                    },
                }

            logger.info(f"Response {response}")
            return encrypt_response(response, aes_key, iv)
