import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "question":
                question = message.get("question", "")
                meeting_id = message.get("meeting_id", "meet_a7b2c9")
                scope = message.get("scope", "current_meeting")
                
                mock_responses = {
                    "支付模块延期是谁提出的？": {
                        "answer": "支付模块延期由张三提出，原因是第三方回调问题尚未解决。",
                        "citations": [
                            {
                                "meeting_id": meeting_id,
                                "chunk_id": "chunk_1001",
                                "speaker": "张三",
                                "start": 0.0,
                                "end": 4.25,
                                "text": "大家好，今天主要对齐一下支付模块的延期问题。",
                            },
                        ],
                    },
                    "谁负责支付回调修复？": {
                        "answer": "王五负责支付回调修复，需要在周四前反馈进度。",
                        "citations": [
                            {
                                "meeting_id": meeting_id,
                                "chunk_id": "chunk_1004",
                                "speaker": "张三",
                                "start": 21.0,
                                "end": 28.3,
                                "text": "同意，王五你负责跟进支付回调的修复，周四前给我反馈。",
                            },
                        ],
                    },
                }
                
                result = mock_responses.get(
                    question,
                    {
                        "answer": f"根据会议记录，关于「{question}」的信息如下：这是模拟流式回答，实际功能需要接入 LLM。",
                        "citations": [
                            {
                                "meeting_id": meeting_id,
                                "chunk_id": "chunk_1001",
                                "speaker": "张三",
                                "start": 0.0,
                                "end": 4.25,
                                "text": "大家好，今天主要对齐一下支付模块的延期问题。",
                            },
                        ],
                    },
                )
                
                await websocket.send_json({"type": "start", "message": ""})
                
                answer = result["answer"]
                chunk_size = 4
                for i in range(0, len(answer), chunk_size):
                    chunk = answer[i:i + chunk_size]
                    await websocket.send_json({"type": "chunk", "message": chunk})
                    await asyncio.sleep(0.05)
                
                await websocket.send_json({
                    "type": "end",
                    "message": "",
                    "citations": result["citations"],
                })
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "code": "QA_FAILED",
            "message": str(e),
        })


@router.websocket("/meetings/{meeting_id}/events")
async def websocket_meeting_events(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    try:
        job_types = ["transcription", "summary", "action", "memory", "graph", "conflict"]
        progress_steps = [0, 20, 40, 60, 80, 100]
        
        for i, job_type in enumerate(job_types):
            for progress in progress_steps:
                await websocket.send_json({
                    "type": "job_progress",
                    "job_id": f"job_{job_type}_{meeting_id}",
                    "job_type": job_type,
                    "status": "running" if progress < 100 else "completed",
                    "progress": progress,
                    "message": f"正在处理 {job_type}... {progress}%",
                })
                await asyncio.sleep(0.3)
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        print(f"Client disconnected from meeting {meeting_id} events")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "code": "EVENTS_FAILED",
            "message": str(e),
        })
