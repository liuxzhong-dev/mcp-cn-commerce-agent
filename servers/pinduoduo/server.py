"""Pinduoduo (拼多多) MCP server — provides tools for reading merchant orders,
products, shop info, after-sale, logistics, reviews, marketing, and affiliate data.

Mock version: Bypasses real PDD network calls and returns realistic mock merchant data.
"""

from __future__ import annotations

import json
import os
import time

from mcp.server.mcpserver import MCPServer

from shared.cn_commerce_base import (
    CommerceMCPBase,
    SignMethod,
    register_common_tools,
)

# ── Pinduoduo client (Mocked) ────────────────────────────────────────────────


class PinduoduoMCP(CommerceMCPBase):
    """Pinduoduo-specific client with built-in Mock data handler."""

    BASE_URL = "https://gw-api.pinduoduo.com/api/router"
    sign_method = SignMethod.MD5

    async def _call(self, api_type: str, biz_params: dict | None = None) -> dict:
        """Intercepts API calls and returns simulated store & order data."""
        biz_params = biz_params or {}

        # 1. 店铺信息
        if api_type == "pdd.mall.info.get":
            return {
                "mall_info_get_response": {
                    "mall_id": 888888,
                    "mall_name": "雅致女装精品店",
                    "logo": "https://img.pinduoduo.com/mock_logo.jpg",
                    "merchant_type": 1,
                    "status": 1,
                    "category": "女士精品服装 / 衬衣"
                }
            }

        # 2. 订单列表
        elif api_type == "pdd.order.list.get":
            return {
                "order_list_get_response": {
                    "total_count": 3,
                    "order_list": [
                        {
                            "order_sn": "PDD20260911001",
                            "goods_name": "【爆款】法式复古真丝质感白衬衫女士长袖",
                            "goods_price": 199.00,
                            "order_amount": 199.00,
                            "order_status": 1,  # 1: 待发货
                            "order_status_str": "待发货",
                            "created_at": "2026-09-11 10:15:00",
                            "buyer_memo": "麻烦尽快发货，着急穿！"
                        },
                        {
                            "order_sn": "PDD20260910002",
                            "goods_name": "韩版垂感显瘦百搭职业女士衬衣",
                            "goods_price": 128.00,
                            "order_amount": 128.00,
                            "order_status": 2,  # 2: 已发货
                            "order_status_str": "已发货",
                            "created_at": "2026-09-10 14:30:00",
                            "buyer_memo": ""
                        },
                        {
                            "order_sn": "PDD20260909003",
                            "goods_name": "设计感小众温柔风桑蚕丝短袖衬衫",
                            "goods_price": 258.00,
                            "order_amount": 258.00,
                            "order_status": 3,  # 3: 已签收
                            "order_status_str": "已签收",
                            "created_at": "2026-09-09 09:20:00",
                            "buyer_memo": "请发顺丰"
                        }
                    ]
                }
            }

        # 3. 订单详情
        elif api_type == "pdd.order.information.get":
            order_sn = biz_params.get("order_sn", "PDD20260911001")
            return {
                "order_info_get_response": {
                    "order_info": {
                        "order_sn": order_sn,
                        "goods_name": "【爆款】法式复古真丝质感白衬衫女士长袖",
                        "goods_price": 199.00,
                        "pay_amount": 199.00,
                        "order_status": 1,
                        "order_status_str": "待发货",
                        "receiver_name": "张女士",
                        "receiver_phone": "138****8888",
                        "receiver_address": "浙江省杭州市西湖区**路88号",
                        "created_at": "2026-09-11 10:15:00"
                    }
                }
            }

        # 4. 商品列表
        elif api_type in ("pdd.goods.list.get", "pdd.goods.search"):
            return {
                "goods_list_get_response": {
                    "total_count": 3,
                    "goods_list": [
                        {
                            "goods_id": "1001",
                            "goods_name": "【爆款】法式复古真丝质感白衬衫女士长袖",
                            "price": 199.00,
                            "sold_quantity": 320,
                            "goods_quantity": 500,
                            "is_onsale": 1
                        },
                        {
                            "goods_id": "1002",
                            "goods_name": "韩版垂感显瘦百搭职业女士衬衣",
                            "price": 128.00,
                            "sold_quantity": 580,
                            "goods_quantity": 200,
                            "is_onsale": 1
                        },
                        {
                            "goods_id": "1003",
                            "goods_name": "设计感小众温柔风桑蚕丝短袖衬衫",
                            "price": 258.00,
                            "sold_quantity": 150,
                            "goods_quantity": 100,
                            "is_onsale": 1
                        }
                    ]
                }
            }

        # 5. 商品评价
        elif api_type == "pdd.goods.comments.get":
            return {
                "goods_comments_get_response": {
                    "total_count": 2,
                    "comment_list": [
                        {
                            "comment_id": "C001",
                            "name": "m***8",
                            "comment": "衣服收到太惊喜了！衬衣面料很有质感，穿上特别显瘦显气质，非常满意！",
                            "score": 5,
                            "time": "2026-09-10"
                        },
                        {
                            "comment_id": "C002",
                            "name": "y***6",
                            "comment": "版型很好看，上身高级，洗了也没有缩水变质，推荐购买。",
                            "score": 5,
                            "time": "2026-09-09"
                        }
                    ]
                }
            }

        # 6. 售后/退款
        elif api_type == "pdd.refund.list.get":
            return {
                "refund_list_get_response": {
                    "total_count": 1,
                    "refund_list": [
                        {
                            "refund_id": "RF20260910001",
                            "order_sn": "PDD20260908005",
                            "goods_name": "韩版垂感显瘦百搭职业女士衬衣",
                            "refund_amount": 128.00,
                            "after_sales_type": 1,  # 仅退款
                            "refund_status": 1,     # 审核中
                            "reason": "拍错尺码/颜色"
                        }
                    ]
                }
            }

        # 7. 物流信息
        elif api_type == "pdd.logistics.trace.query":
            return {
                "logistics_trace_query_response": {
                    "shipping_company": "顺丰速运",
                    "tracking_number": "SF13890281390",
                    "status": "已揽收",
                    "traces": [
                        {"time": "2026-09-10 16:00:00", "status": "商家已发货"},
                        {"time": "2026-09-10 18:30:00", "status": "顺丰速运 已收取快件"}
                    ]
                }
            }

        # 兜底默认 Mock
        return {
            "result": "success",
            "mock": True,
            "api_type": api_type,
            "biz_params": biz_params
        }


# ── Instantiate client from env (Mock safely) ─────────────────────────────


def _create_pinduoduo_client() -> PinduoduoMCP:
    """Create pinduoduo client with fallback to mock values."""
    return PinduoduoMCP(
        app_key=os.environ.get("PINDUODUO_CLIENT_ID", "mock_client_id"),
        app_secret=os.environ.get("PINDUODUO_CLIENT_SECRET", "mock_client_secret"),
        access_token=os.environ.get("PINDUODUO_ACCESS_TOKEN", "mock_access_token_12345"),
    )


pdd = _create_pinduoduo_client()


# ── MCP server ─────────────────────────────────────────────────────────────

mcp = MCPServer("mcp-cn-pinduoduo")


# ═══════════════════════════════════════════════════════════════════════════════
# 订单 (Orders)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def get_order_list(
    start_time: str,
    end_time: str,
    order_status: str = "",
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Query order list by time range and optional status."""
    biz_params: dict = {
        "start_created_at": start_time,
        "end_created_at": end_time,
        "page": str(page),
        "page_size": str(page_size),
    }
    if order_status:
        biz_params["order_status"] = order_status

    result = await pdd._call("pdd.order.list.get", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_order_detail(order_sn: str) -> str:
    """Get full details of a single order."""
    biz_params = {"order_sn": order_sn}
    result = await pdd._call("pdd.order.information.get", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 商品 (Products)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def get_product_list(
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Get product (goods) list with basic info."""
    biz_params = {
        "page": str(page),
        "page_size": str(page_size),
    }
    result = await pdd._call("pdd.goods.list.get", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_product_detail(goods_id: str) -> str:
    """Get full details of a single product by goods ID."""
    biz_params = {"goods_id": goods_id}
    result = await pdd._call("pdd.goods.detail.get", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def search_products(
    keyword: str,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Search products by keyword."""
    biz_params = {
        "keyword": keyword,
        "page": str(page),
        "page_size": str(page_size),
    }
    result = await pdd._call("pdd.goods.search", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 售后 (After-Sale)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def get_refund_list(
    start_time: str,
    end_time: str,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Query refund (after-sale) list by time range."""
    biz_params = {
        "start_created_at": start_time,
        "end_created_at": end_time,
        "page": str(page),
        "page_size": str(page_size),
    }
    result = await pdd._call("pdd.refund.list.get", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_refund_detail(refund_id: str) -> str:
    """Get full details of a single refund record."""
    biz_params = {"refund_id": refund_id}
    result = await pdd._call("pdd.refund.information.get", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 物流 (Logistics)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def get_logistics_tracking(order_sn: str) -> str:
    """Get logistics tracking information for an order."""
    biz_params = {"order_sn": order_sn}
    result = await pdd._call("pdd.logistics.trace.query", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def list_logistics_companies() -> str:
    """List all available logistics companies on Pinduoduo platform."""
    result = await pdd._call("pdd.logistics.companies.get", {})
    return json.dumps(result, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 评价 (Reviews)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def get_review_list(
    goods_id: str,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Query product review (comment) list by goods ID."""
    biz_params = {
        "goods_id": goods_id,
        "page": str(page),
        "page_size": str(page_size),
    }
    result = await pdd._call("pdd.goods.comments.get", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 店铺 (Shop)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def get_shop_info() -> str:
    """Get mall/shop basic information for the authenticated merchant."""
    result = await pdd._call("pdd.mall.info.get", {})
    return json.dumps(result, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 营销 (Marketing)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def list_promotions(
    page: int = 1,
    page_size: int = 20,
) -> str:
    """List promotion activities for the authenticated shop."""
    biz_params = {
        "page": str(page),
        "page_size": str(page_size),
    }
    result = await pdd._call("pdd.promotion.list.get", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 多多客 (Affiliate)
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def search_affiliate_goods(
    keyword: str,
    page: int = 1,
    page_size: int = 20,
) -> str:
    """Search affiliate (多多客) goods by keyword."""
    biz_params = {
        "keyword": keyword,
        "page": str(page),
        "page_size": str(page_size),
    }
    result = await pdd._call("pdd.ddk.goods.search", biz_params)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ── Cross-platform operational tools ──────────────────────────────────────────
register_common_tools(mcp, pdd)


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    """Entry point for 'mcp-cn-pinduoduo' console script."""
    mcp.run()


if __name__ == "__main__":
    main()