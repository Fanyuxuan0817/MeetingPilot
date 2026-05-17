from fastapi import APIRouter

from app.schemas.qa import QARequest, QAResponse

router = APIRouter()


@router.post("/qa", response_model=QAResponse)
async def ask_question(data: QARequest):
    mock_qa_pairs = {
        "支付模块延期是谁提出的？": {
            "answer": "支付模块延期由张三提出，原因是第三方回调问题尚未解决。",
            "citations": [
                {
                    "meeting_id": data.meeting_id or "meet_a7b2c9",
                    "chunk_id": "chunk_1001",
                    "speaker": "张三",
                    "start": 0.0,
                    "end": 4.25,
                    "text": "大家好，今天主要对齐一下支付模块的延期问题。",
                },
                {
                    "meeting_id": data.meeting_id or "meet_a7b2c9",
                    "chunk_id": "chunk_1002",
                    "speaker": "李四",
                    "start": 4.5,
                    "end": 12.8,
                    "text": "支付模块由于第三方回调问题，需要延期到周五完成。",
                },
            ],
        },
        "谁负责支付回调修复？": {
            "answer": "王五负责支付回调修复，需要在周四前反馈进度。",
            "citations": [
                {
                    "meeting_id": data.meeting_id or "meet_a7b2c9",
                    "chunk_id": "chunk_1004",
                    "speaker": "张三",
                    "start": 21.0,
                    "end": 28.3,
                    "text": "同意，王五你负责跟进支付回调的修复，周四前给我反馈。",
                },
            ],
        },
        "上线时间定了吗？": {
            "answer": "上线时间已从周三推迟到周五，等待支付模块修复后一起上线。",
            "citations": [
                {
                    "meeting_id": data.meeting_id or "meet_a7b2c9",
                    "chunk_id": "chunk_1003",
                    "speaker": "王五",
                    "start": 13.0,
                    "end": 20.5,
                    "text": "那原定周三上线的计划需要调整了，建议推迟到周五一起上线。",
                },
            ],
        },
    }
    
    result = mock_qa_pairs.get(
        data.question,
        {
            "answer": f"根据会议记录，关于「{data.question}」的信息如下：这是模拟回答，实际功能需要接入 LLM。",
            "citations": [
                {
                    "meeting_id": data.meeting_id or "meet_a7b2c9",
                    "chunk_id": "chunk_1001",
                    "speaker": "张三",
                    "start": 0.0,
                    "end": 4.25,
                    "text": "大家好，今天主要对齐一下支付模块的延期问题。",
                },
            ],
        },
    )
    
    return result


@router.post("/memory/search")
async def search_memory(query: str, limit: int = 5, filters: dict | None = None):
    return {
        "items": [
            {
                "meeting_id": "meet_b8c1d2",
                "meeting_title": "支付系统技术评审",
                "chunk_id": "chunk_8801",
                "speaker": "李四",
                "start": 230.0,
                "end": 245.0,
                "text": "支付回调存在偶发失败，需要延期排查。",
                "score": 0.89,
            },
            {
                "meeting_id": "meet_a7b2c9",
                "meeting_title": "产品迭代周会",
                "chunk_id": "chunk_1002",
                "speaker": "李四",
                "start": 4.5,
                "end": 12.8,
                "text": "支付模块由于第三方回调问题，需要延期到周五完成。",
                "score": 0.85,
            },
        ],
    }


@router.get("/meetings/{meeting_id}/graph")
async def get_meeting_graph(meeting_id: str):
    return {
        "nodes": [
            {"id": "person_zhangsan", "label": "张三", "type": "person"},
            {"id": "person_lisi", "label": "李四", "type": "person"},
            {"id": "person_wangwu", "label": "王五", "type": "person"},
            {"id": "task_payment_callback", "label": "修复支付回调", "type": "task"},
            {"id": "task_update_doc", "label": "更新上线计划文档", "type": "task"},
            {"id": "topic_payment_module", "label": "支付模块", "type": "topic"},
            {"id": "topic_launch_date", "label": "上线时间", "type": "topic"},
        ],
        "edges": [
            {"source": "person_zhangsan", "target": "task_update_doc", "type": "负责"},
            {"source": "person_wangwu", "target": "task_payment_callback", "type": "负责"},
            {"source": "person_zhangsan", "target": "topic_payment_module", "type": "提及"},
            {"source": "person_lisi", "target": "topic_payment_module", "type": "提及"},
            {"source": "person_wangwu", "target": "topic_launch_date", "type": "提议"},
        ],
    }


@router.post("/graph/query")
async def query_graph(question: str):
    return {
        "answer": "最近三次会议中，张三负责支付回调修复跟进、上线计划文档更新和接口联调协调。",
        "nodes": [
            {"id": "person_zhangsan", "label": "张三", "type": "person"},
            {"id": "task_payment_callback", "label": "修复支付回调", "type": "task"},
            {"id": "task_update_doc", "label": "更新上线计划文档", "type": "task"},
        ],
        "edges": [
            {"source": "person_zhangsan", "target": "task_payment_callback", "type": "跟进"},
            {"source": "person_zhangsan", "target": "task_update_doc", "type": "负责"},
        ],
    }
