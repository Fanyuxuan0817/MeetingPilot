#!/usr/bin/env python3
"""
前后端数据一致性测试脚本

测试内容:
  1. Pydantic 模型字段 <-> TypeScript 接口字段（名称、可空性、必填性）
  2. Python Enum <-> TypeScript Enum（枚举值完全一致）
  3. API 端点响应结构验证（FastAPI TestClient）

运行方式:
    cd backend
    python -m pytest tests/test_consistency.py -v
    # 或
    python tests/test_consistency.py

注意事项：
    正则限制：脚本使用正则表达式解析 TS 文件，因此在编写 TS 接口时，
    请保持标准的 export interface Name { ... } 格式，不要写过于复杂的嵌套定义。
"""

import re
import sys
import types
from enum import Enum
from pathlib import Path
from typing import Annotated, Union, get_args, get_origin

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_TYPES_DIR = (
    PROJECT_ROOT / "frontend" / "meetingPilot-frontend" / "src" / "types"
)

sys.path.insert(0, str(BACKEND_DIR))

from pydantic import BaseModel

from app.schemas.action_item import (
    ActionItemBase,
    ActionItemCreate,
    ActionItemRead,
    ActionItemUpdate,
    ActionStatus,
    Priority,
)
from app.schemas.common import ErrorResponse, JobResponse, JobStatus, PaginationResponse
from app.schemas.decision import ConflictLevel, DecisionConflictRead, DecisionRead
from app.schemas.meeting import (
    MeetingBase,
    MeetingCreate,
    MeetingRead,
    MeetingStatus,
    MeetingUpdate,
)
from app.schemas.qa import Citation, QARequest, QAResponse, WSMessage
from app.schemas.summary import (
    DecisionShort,
    Risk,
    RiskLevel,
    SummaryDetail,
    SummaryRead,
    Topic,
)
from app.schemas.transcript import (
    TranscriptChunkBase,
    TranscriptChunkRead,
    TranscriptChunkUpdate,
    TranscriptListRead,
)

from fastapi.testclient import TestClient
from app.main import app


# ═══════════════════════════════════════════════════════════════════════
# 辅助函数: Pydantic 模型分析
# ═══════════════════════════════════════════════════════════════════════

def unwrap_annotated(tp):
    if get_origin(tp) is Annotated:
        return get_args(tp)[0]
    return tp


def is_nullable(tp) -> bool:
    tp = unwrap_annotated(tp)
    origin = get_origin(tp)
    if origin is Union:
        return type(None) in get_args(tp)
    if isinstance(tp, types.UnionType):
        return type(None) in get_args(tp)
    return False


def extract_pydantic_fields(model: type[BaseModel]) -> dict:
    result = {}
    for name, field_info in model.model_fields.items():
        tp = field_info.annotation
        result[name] = {
            "nullable": is_nullable(tp),
            "required": field_info.is_required(),
        }
    return result


def extract_enum_values(enum_cls: type[Enum]) -> dict[str, str]:
    return {member.name: member.value for member in enum_cls}


# ═══════════════════════════════════════════════════════════════════════
# 辅助函数: TypeScript 文件解析
# ═══════════════════════════════════════════════════════════════════════

def parse_all_ts_files() -> tuple[dict, dict]:
    all_enums: dict[str, dict[str, str]] = {}
    all_interfaces: dict[str, dict] = {}

    for ts_file in FRONTEND_TYPES_DIR.glob("*.ts"):
        if ts_file.name == "index.ts":
            continue
        text = ts_file.read_text(encoding="utf-8")
        all_enums.update(_parse_ts_enums(text))
        all_interfaces.update(_parse_ts_interfaces(text))

    return all_enums, all_interfaces


def _parse_ts_enums(text: str) -> dict[str, dict[str, str]]:
    enums = {}
    for m in re.finditer(r"export\s+enum\s+(\w+)\s*\{([^}]+)\}", text):
        name = m.group(1)
        body = m.group(2)
        values = {}
        for member in re.finditer(r"(\w+)\s*=\s*'([^']*)'", body):
            values[member.group(1)] = member.group(2)
        enums[name] = values
    return enums


def _parse_ts_interfaces(text: str) -> dict[str, dict]:
    interfaces = {}
    for m in re.finditer(
        r"export\s+interface\s+(\w+)(?:<[^>]+>)?(?:\s+extends\s+(\w+))?\s*\{([^}]*)\}",
        text,
    ):
        name = m.group(1)
        extends = m.group(2)
        body = m.group(3)
        fields = {}
        for fm in re.finditer(r"^\s*(\w+)(\??):\s*(.+?)\s*$", body, re.MULTILINE):
            field_name = fm.group(1)
            optional = fm.group(2) == "?"
            raw_type = fm.group(3).strip()
            nullable = "| null" in raw_type
            fields[field_name] = {
                "optional": optional,
                "nullable": nullable,
                "raw_type": raw_type,
            }
        interfaces[name] = {
            "extends": extends,
            "fields": fields,
        }
    return interfaces


def resolve_ts_fields(interface_name: str, all_interfaces: dict) -> dict:
    iface = all_interfaces.get(interface_name)
    if not iface:
        return {}
    fields = {}
    if iface["extends"]:
        fields.update(resolve_ts_fields(iface["extends"], all_interfaces))
    fields.update(iface["fields"])
    return fields


# ═══════════════════════════════════════════════════════════════════════
# 测试 1: Enum 值对比
# ═══════════════════════════════════════════════════════════════════════

ENUM_MAP = [
    (JobStatus, "JobStatus"),
    (MeetingStatus, "MeetingStatus"),
    (RiskLevel, "RiskLevel"),
    (ActionStatus, "ActionStatus"),
    (Priority, "Priority"),
    (ConflictLevel, "ConflictLevel"),
]


def test_enums(all_ts_enums: dict) -> list[str]:
    errors = []
    for py_enum, ts_name in ENUM_MAP:
        py_values = extract_enum_values(py_enum)
        ts_values = all_ts_enums.get(ts_name)

        if ts_values is None:
            errors.append(f"[ENUM] {ts_name}: TypeScript 中未找到对应 enum")
            continue

        py_keys = set(py_values.keys())
        ts_keys = set(ts_values.keys())

        missing_in_ts = py_keys - ts_keys
        extra_in_ts = ts_keys - py_keys

        if missing_in_ts:
            errors.append(
                f"[ENUM] {ts_name}: TS 缺少成员 {missing_in_ts}"
            )
        if extra_in_ts:
            errors.append(
                f"[ENUM] {ts_name}: TS 多出成员 {extra_in_ts}"
            )

        for key in py_keys & ts_keys:
            if py_values[key] != ts_values[key]:
                errors.append(
                    f"[ENUM] {ts_name}.{key}: Python='{py_values[key]}' vs TS='{ts_values[key]}'"
                )

    return errors


# ═══════════════════════════════════════════════════════════════════════
# 测试 2: Interface 字段对比
# ═══════════════════════════════════════════════════════════════════════

INTERFACE_MAP = [
    (JobResponse, "JobResponse"),
    (ErrorResponse, "ErrorResponse"),
    (MeetingBase, "MeetingBase"),
    (MeetingCreate, "MeetingCreate"),
    (MeetingUpdate, "MeetingUpdate"),
    (MeetingRead, "MeetingRead"),
    (TranscriptChunkBase, "TranscriptChunkBase"),
    (TranscriptChunkUpdate, "TranscriptChunkUpdate"),
    (TranscriptChunkRead, "TranscriptChunkRead"),
    (TranscriptListRead, "TranscriptListRead"),
    (Topic, "Topic"),
    (DecisionShort, "DecisionShort"),
    (Risk, "Risk"),
    (SummaryDetail, "SummaryDetail"),
    (SummaryRead, "SummaryRead"),
    (ActionItemBase, "ActionItemBase"),
    (ActionItemCreate, "ActionItemCreate"),
    (ActionItemUpdate, "ActionItemUpdate"),
    (ActionItemRead, "ActionItemRead"),
    (DecisionRead, "DecisionRead"),
    (DecisionConflictRead, "DecisionConflictRead"),
    (Citation, "Citation"),
    (QARequest, "QARequest"),
    (QAResponse, "QAResponse"),
    (WSMessage, "WSMessage"),
]


def test_interfaces(all_ts_interfaces: dict) -> list[str]:
    errors = []
    for py_model, ts_name in INTERFACE_MAP:
        py_fields = extract_pydantic_fields(py_model)
        ts_fields = resolve_ts_fields(ts_name, all_ts_interfaces)

        if not ts_fields and ts_name not in all_ts_interfaces:
            errors.append(f"[IFACE] {ts_name}: TypeScript 中未找到对应 interface")
            continue

        py_names = set(py_fields.keys())
        ts_names = set(ts_fields.keys())

        missing_in_ts = py_names - ts_names
        extra_in_ts = ts_names - py_names

        if missing_in_ts:
            errors.append(
                f"[IFACE] {ts_name}: TS 缺少字段 {missing_in_ts}"
            )
        if extra_in_ts:
            errors.append(
                f"[IFACE] {ts_name}: TS 多出字段 {extra_in_ts}"
            )

        for name in py_names & ts_names:
            py_nullable = py_fields[name]["nullable"]
            ts_nullable = ts_fields[name]["nullable"]
            if py_nullable and not ts_nullable:
                errors.append(
                    f"[IFACE] {ts_name}.{name}: Python 可空但 TS 不可空"
                )
            if not py_nullable and ts_nullable:
                errors.append(
                    f"[IFACE] {ts_name}.{name}: Python 不可空但 TS 可空 (| null)"
                )

            py_required = py_fields[name]["required"]
            ts_optional = ts_fields[name]["optional"]
            if py_required and ts_optional:
                errors.append(
                    f"[IFACE] {ts_name}.{name}: Python 必填但 TS 可选 (?)"
                )
            if not py_required and not ts_optional:
                pass

    return errors


# ═══════════════════════════════════════════════════════════════════════
# 测试 3: API 端点响应结构验证
# ═══════════════════════════════════════════════════════════════════════

MEETING_ID = "meet_a7b2c9"


def _expected_keys_from_model(model: type[BaseModel]) -> set[str]:
    return set(model.model_fields.keys())


def _expected_keys_from_ts(ts_name: str, all_ts_interfaces: dict) -> set[str]:
    return set(resolve_ts_fields(ts_name, all_ts_interfaces).keys())


def test_api_responses(all_ts_interfaces: dict) -> list[str]:
    errors = []
    client = TestClient(app)

    endpoints = [
        {
            "method": "GET",
            "url": "/api/v1/meetings",
            "params": {"page": 1, "size": 10},
            "status": 200,
            "ts_response_type": "PaginationResponse",
            "note": "列表响应检查 items 内元素结构",
        },
        {
            "method": "GET",
            "url": f"/api/v1/meetings/{MEETING_ID}",
            "params": None,
            "status": 200,
            "py_model": MeetingRead,
        },
        {
            "method": "GET",
            "url": f"/api/v1/meetings/{MEETING_ID}/transcripts",
            "params": None,
            "status": 200,
            "py_model": TranscriptListRead,
        },
        {
            "method": "GET",
            "url": "/api/v1/transcripts/chunk_1001",
            "params": None,
            "status": 200,
            "py_model": TranscriptChunkRead,
        },
        {
            "method": "GET",
            "url": f"/api/v1/meetings/{MEETING_ID}/summary",
            "params": None,
            "status": 200,
            "py_model": SummaryRead,
        },
        {
            "method": "GET",
            "url": f"/api/v1/meetings/{MEETING_ID}/actions",
            "params": None,
            "status": 200,
            "ts_response_type": "ActionListResponse",
        },
        {
            "method": "GET",
            "url": f"/api/v1/meetings/{MEETING_ID}/decisions",
            "params": None,
            "status": 200,
            "ts_response_type": "DecisionListResponse",
        },
        {
            "method": "GET",
            "url": f"/api/v1/meetings/{MEETING_ID}/conflicts",
            "params": None,
            "status": 200,
            "ts_response_type": "ConflictListResponse",
        },
        {
            "method": "GET",
            "url": f"/api/v1/meetings/{MEETING_ID}/graph",
            "params": None,
            "status": 200,
            "ts_response_type": "MeetingGraphResponse",
        },
        {
            "method": "GET",
            "url": f"/api/v1/meetings/{MEETING_ID}/jobs",
            "params": None,
            "status": 200,
            "ts_response_type": "MeetingJobsResponse",
        },
        {
            "method": "POST",
            "url": "/api/v1/qa",
            "json": {"question": "测试问题", "meeting_id": MEETING_ID, "scope": "current_meeting"},
            "status": 200,
            "py_model": QAResponse,
        },
        {
            "method": "POST",
            "url": "/api/v1/meetings",
            "json": {"title": "测试会议", "started_at": "2025-01-01T00:00:00Z"},
            "status": 201,
            "py_model": MeetingRead,
        },
        {
            "method": "PATCH",
            "url": f"/api/v1/meetings/{MEETING_ID}",
            "json": {"title": "更新标题"},
            "status": 200,
            "py_model": MeetingRead,
        },
        {
            "method": "POST",
            "url": f"/api/v1/meetings/{MEETING_ID}/transcribe",
            "json": None,
            "status": 202,
            "py_model": JobResponse,
        },
        {
            "method": "POST",
            "url": f"/api/v1/meetings/{MEETING_ID}/summary/generate",
            "json": None,
            "status": 202,
            "py_model": JobResponse,
        },
        {
            "method": "POST",
            "url": f"/api/v1/meetings/{MEETING_ID}/actions",
            "json": {"task": "测试任务", "owner": "张三"},
            "status": 201,
            "py_model": ActionItemRead,
        },
        {
            "method": "PATCH",
            "url": "/api/v1/actions/act_501",
            "json": {"status": "doing"},
            "status": 200,
            "py_model": ActionItemRead,
        },
        {
            "method": "POST",
            "url": f"/api/v1/meetings/{MEETING_ID}/actions/extract",
            "json": None,
            "status": 202,
            "py_model": JobResponse,
        },
        {
            "method": "POST",
            "url": "/api/v1/actions/act_501/sync/feishu",
            "json": None,
            "status": 200,
            "ts_response_type": "FeishuSyncResponse",
        },
        {
            "method": "POST",
            "url": f"/api/v1/meetings/{MEETING_ID}/conflicts/detect",
            "json": None,
            "status": 202,
            "py_model": JobResponse,
        },
        {
            "method": "POST",
            "url": f"/api/v1/meetings/{MEETING_ID}/agents/run",
            "json": {"agents": ["summary"]},
            "status": 202,
            "py_model": JobResponse,
        },
        {
            "method": "POST",
            "url": "/api/v1/memory/search",
            "params": {"query": "支付"},
            "json": None,
            "status": 200,
            "ts_response_type": "MemorySearchResponse",
        },
        {
            "method": "POST",
            "url": "/api/v1/graph/query",
            "params": {"question": "谁负责支付回调修复？"},
            "json": None,
            "status": 200,
            "ts_response_type": "GraphQueryResponse",
        },
        {
            "method": "DELETE",
            "url": f"/api/v1/meetings/{MEETING_ID}",
            "params": None,
            "status": 204,
        },
        {
            "method": "DELETE",
            "url": "/api/v1/actions/act_501",
            "params": None,
            "status": 204,
        },
    ]

    for ep in endpoints:
        method = ep["method"]
        url = ep["url"]
        label = f"{method} {url}"

        try:
            if method == "GET":
                resp = client.get(url, params=ep.get("params"))
            elif method == "POST":
                resp = client.post(url, json=ep.get("json"), params=ep.get("params"))
            elif method == "PATCH":
                resp = client.patch(url, json=ep.get("json"))
            elif method == "DELETE":
                resp = client.delete(url)
            else:
                continue
        except Exception as e:
            errors.append(f"[API] {label}: 请求异常 - {e}")
            continue

        if resp.status_code != ep["status"]:
            errors.append(
                f"[API] {label}: 状态码 {resp.status_code} != 期望 {ep['status']}"
            )
            continue

        if ep["status"] == 204:
            continue

        body = resp.json()

        if "py_model" in ep:
            expected = _expected_keys_from_model(ep["py_model"])
            model_name = ep["py_model"].__name__
        elif "ts_response_type" in ep:
            expected = _expected_keys_from_ts(ep["ts_response_type"], all_ts_interfaces)
            model_name = ep["ts_response_type"]
        else:
            continue

        actual_top_keys = set(body.keys())

        missing = expected - actual_top_keys
        extra = actual_top_keys - expected

        if missing:
            errors.append(
                f"[API] {label}: 响应缺少字段 {missing} (期望来自 {model_name})"
            )
        if extra:
            errors.append(
                f"[API] {label}: 响应多出字段 {extra} (期望来自 {model_name})"
            )

        if "py_model" in ep:
            try:
                ep["py_model"].model_validate(body)
            except Exception as e:
                errors.append(
                    f"[API] {label}: Pydantic 验证失败 - {e}"
                )

        if ep.get("ts_response_type") == "PaginationResponse":
            items = body.get("items", [])
            if items:
                item_keys = set(items[0].keys())
                meeting_read_keys = _expected_keys_from_model(MeetingRead)
                missing_item = meeting_read_keys - item_keys
                extra_item = item_keys - meeting_read_keys
                if missing_item:
                    errors.append(
                        f"[API] {label}: items[] 缺少字段 {missing_item}"
                    )
                if extra_item:
                    errors.append(
                        f"[API] {label}: items[] 多出字段 {extra_item}"
                    )

        if ep.get("ts_response_type") in (
            "ActionListResponse",
            "DecisionListResponse",
            "ConflictListResponse",
        ):
            ts_name = ep["ts_response_type"]
            ts_fields = resolve_ts_fields(ts_name, all_ts_interfaces)
            items_field = ts_fields.get("items", {})
            items_type_raw = items_field.get("raw_type", "")

            item_ts_name = items_type_raw.replace("[]", "").strip()
            item_expected = _expected_keys_from_ts(item_ts_name, all_ts_interfaces)

            items = body.get("items", [])
            if items:
                item_keys = set(items[0].keys())
                missing_item = item_expected - item_keys
                extra_item = item_keys - item_expected
                if missing_item:
                    errors.append(
                        f"[API] {label}: items[] 缺少字段 {missing_item} (期望来自 {item_ts_name})"
                    )
                if extra_item:
                    errors.append(
                        f"[API] {label}: items[] 多出字段 {extra_item} (期望来自 {item_ts_name})"
                    )

        if ep.get("ts_response_type") == "MemorySearchResponse":
            items = body.get("items", [])
            if items:
                item_expected = _expected_keys_from_ts("MemorySearchResultItem", all_ts_interfaces)
                item_keys = set(items[0].keys())
                missing_item = item_expected - item_keys
                extra_item = item_keys - item_expected
                if missing_item:
                    errors.append(
                        f"[API] {label}: items[] 缺少字段 {missing_item} (期望来自 MemorySearchResultItem)"
                    )
                if extra_item:
                    errors.append(
                        f"[API] {label}: items[] 多出字段 {extra_item} (期望来自 MemorySearchResultItem)"
                    )

        if ep.get("ts_response_type") in ("MeetingGraphResponse", "GraphQueryResponse"):
            ts_name = ep["ts_response_type"]
            ts_fields = resolve_ts_fields(ts_name, all_ts_interfaces)

            for collection_key in ("nodes", "edges"):
                collection = body.get(collection_key, [])
                if not collection:
                    continue
                item_type_raw = ts_fields.get(collection_key, {}).get("raw_type", "")
                item_ts_name = item_type_raw.replace("[]", "").strip()
                item_expected = _expected_keys_from_ts(item_ts_name, all_ts_interfaces)
                item_keys = set(collection[0].keys())
                missing_item = item_expected - item_keys
                extra_item = item_keys - item_expected
                if missing_item:
                    errors.append(
                        f"[API] {label}: {collection_key}[] 缺少字段 {missing_item} (期望来自 {item_ts_name})"
                    )
                if extra_item:
                    errors.append(
                        f"[API] {label}: {collection_key}[] 多出字段 {extra_item} (期望来自 {item_ts_name})"
                    )

        if ep.get("ts_response_type") == "MeetingJobsResponse":
            items = body.get("jobs", [])
            if items:
                item_expected = _expected_keys_from_ts("MeetingJobItem", all_ts_interfaces)
                item_keys = set(items[0].keys())
                missing_item = item_expected - item_keys
                extra_item = item_keys - item_expected
                if missing_item:
                    errors.append(
                        f"[API] {label}: jobs[] 缺少字段 {missing_item} (期望来自 MeetingJobItem)"
                    )
                if extra_item:
                    errors.append(
                        f"[API] {label}: jobs[] 多出字段 {extra_item} (期望来自 MeetingJobItem)"
                    )

    return errors


# ═══════════════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  前后端数据一致性测试")
    print("=" * 70)

    all_errors = []

    # ── 解析 TypeScript 文件 ──────────────────────────────────────────
    print("\n>> 解析 TypeScript 类型文件 ...")
    ts_enums, ts_interfaces = parse_all_ts_files()
    print(f"   找到 {len(ts_enums)} 个 enum, {len(ts_interfaces)} 个 interface")

    # ── 测试 1: Enum 对比 ─────────────────────────────────────────────
    print("\n>> 测试 1: Enum 值对比 (Python <-> TypeScript)")
    enum_errors = test_enums(ts_enums)
    if enum_errors:
        for e in enum_errors:
            print(f"   FAIL  {e}")
        all_errors.extend(enum_errors)
    else:
        print(f"   PASS  全部 {len(ENUM_MAP)} 个 enum 一致")

    # ── 测试 2: Interface 字段对比 ────────────────────────────────────
    print("\n>> 测试 2: Interface 字段对比 (Python <-> TypeScript)")
    iface_errors = test_interfaces(ts_interfaces)
    if iface_errors:
        for e in iface_errors:
            print(f"   FAIL  {e}")
        all_errors.extend(iface_errors)
    else:
        print(f"   PASS  全部 {len(INTERFACE_MAP)} 个 interface 一致")

    # ── 测试 3: API 响应结构验证 ──────────────────────────────────────
    print("\n>> 测试 3: API 端点响应结构验证 (TestClient)")
    api_errors = test_api_responses(ts_interfaces)
    if api_errors:
        for e in api_errors:
            print(f"   FAIL  {e}")
        all_errors.extend(api_errors)
    else:
        print("   PASS  全部 API 端点响应结构一致")

    # ── 汇总 ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    if all_errors:
        print(f"  RESULT: FAIL  ({len(all_errors)} 个不一致)")
        sys.exit(1)
    else:
        print("  RESULT: PASS  前后端数据完全一致")
        sys.exit(0)


if __name__ == "__main__":
    main()
