## 📌 后端“真转录”主干道

### 步骤 1：设计持久化数据模型 (PostgreSQL)

我们需要在 `backend/app/models/` 下建立会议主表和转录片段从表。为了支撑后续可能的向量检索（RAG），建议预留自增主键或 UUID。

在 `backend/app/models/meeting.py` 中：

```python
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
from app.database import Base  # 假设你的Base在这里

class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), default="未命名会议")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 一对多关联
    chunks: Mapped[list["TranscriptChunk"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )

```

在 `backend/app/models/transcript.py` 中：

```python
from sqlalchemy import String, Float, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from app.database import Base

class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"))
    
    # 核心四个字段
    start: Mapped[float] = mapped_column(Float, nullable=False)  # 起始时间(秒)
    end: Mapped[float] = mapped_column(Float, nullable=False)    # 结束时间(秒)
    speaker: Mapped[str] = mapped_column(String(50), default="Unknown")
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # 反向关联
    meeting: Mapped["Meeting"] = relationship(back_populates="chunks")

```

#### Alembic 迁移命令

确认在 `env.py` 中导入了上述模型后，在项目根目录执行：

```bash
alembic revision --autogenerate -m "add_meeting_and_transcript_models"
alembic upgrade head

```

---

### 步骤 2：集成 Faster-Whisper 转录服务

Faster-Whisper 相比 OpenAI 原版 Whisper 提速了 4-4 倍，非常适合本地或私有化部署。我们在 `backend/app/services/transcription_service.py` 中封装它。

> ⚠️ **注意**：模型加载（`WhisperModel`）是 CPU/GPU 密集型操作，**必须声明为单例**，避免每次接口调用都重复加载导致内存溢出。

```python
import os
from loguru import logger
from faster_whisper import WhisperModel
from app.models.transcript import TranscriptChunk

class TranscriptionService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            # 初始化模型，建议先用 base/small 调通流程，生产用 large-v3
            model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
            device = os.getenv("WHISPER_DEVICE", "cpu") # 如果有GPU，改为 "cuda"
            logger.info(f"Loading Faster-Whisper model: {model_size} on {device}...")
            cls._instance.model = WhisperModel(model_size, device=device, compute_type="float32")
            logger.info("Whisper model loaded successfully.")
        return cls._instance

    async def transcribe_audio(self, audio_path: str) -> list[dict]:
        """
        调用 Faster-Whisper 解析音频
        由于 faster-whisper 是同步阻塞的，建议在线程池中运行
        """
        import asyncio
        from functools import partial

        loop = asyncio.get_running_loop()
        # 使用 partial 传参，让同步阻塞函数在默认线程池中运行
        func = partial(self._instance.model.transcribe, audio_path, beam_size=5, word_timestamps=False)
        
        # segments 是一个生成器
        segments, info = await loop.run_in_executor(None, func)
        
        logger.info(f"Detected language '{info.language}' with probability {info.language_probability}")

        chunks = []
        for segment in segments:
            chunks.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "speaker": f"Speaker 1",  # 基础版先写死，第二阶段再接 Diarization 声纹分割
                "content": segment.text.strip()
            })
        return chunks

transcription_service = TranscriptionService()

```

---

### 步骤 3：实现“解析 -> 批量存库”管道

为了防止前台上传音频后长连接超时（Timeout），转录必须是**异步执行**的。这里我们可以利用 FastAPI 自带的 `BackgroundTasks`（如果需要更重的队列，后期可重构为 Celery）。

在 `backend/app/services/pipeline.py` 中：

```python
import os
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.transcription_service import transcription_service
from app.models.transcript import TranscriptChunk

async def run_transcription_pipeline(meeting_id: str, audio_path: str, db_factory):
    """
    后台管道任务：转录音频并批量写入数据库
    :param db_factory: 用于在后台线程/任务中创建独立 DB 会话的工厂函数
    """
    try:
        logger.info(f"Starting async transcription pipeline for meeting: {meeting_id}")
        
        # 1. 产生真实的转录文字
        raw_chunks = await transcription_service.transcribe_audio(audio_path)
        
        # 2. 批量写入数据库 (获取新的独立 session)
        async with db_factory() as db:
            db_chunks = [
                TranscriptChunk(
                    meeting_id=meeting_id,
                    start=chunk["start"],
                    end=chunk["end"],
                    speaker=chunk["speaker"],
                    content=chunk["content"]
                )
                for chunk in raw_chunks
            ]
            db.add_all(db_chunks)
            await db.commit()
            
        logger.info(f"Pipeline finished. Successfully saved {len(raw_chunks)} chunks for meeting: {meeting_id}")
        
    except Exception as e:
        logger.error(f"Pipeline failed for meeting {meeting_id}: {str(e)}")
    finally:
        # 清理临时文件
        if os.path.exists(audio_path):
            os.remove(audio_path)

```

---

### 步骤 4：重构 API 路由，替换 Mock 数据

现在我们将上传接口和获取转录内容的接口切换为真实数据库逻辑。

在 `backend/app/api/endpoints/meetings.py` 中：

```python
import uuid
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db, async_session_factory # 替换为你的真实DB方法
from app.models.meeting import Meeting
from app.models.transcript import TranscriptChunk
from app.services.pipeline import run_transcription_pipeline

router = APIRouter()

@router.post("/meetings/upload")
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. 创建会议记录
    new_meeting = Meeting(title=file.filename.split('.')[0])
    db.add(new_meeting)
    await db.commit()
    await db.refresh(new_meeting)

    # 2. 保存临时音频文件到本地目录
    temp_dir = "/tmp/meeting_audios"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = f"{temp_dir}/{new_meeting.id}_{file.filename}"
    
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. 触发后台异步转录主干道
    background_tasks.add_task(
        run_transcription_pipeline,
        meeting_id=new_meeting.id,
        audio_path=temp_file_path,
        db_factory=async_session_factory  # 传入session工厂以便后台任务自行管理生命周期
    )

    return {"meeting_id": new_meeting.id, "status": "processing", "message": "音频上传成功，后台转录中..."}


@router.get("/meetings/{id}/transcripts")
async def get_meeting_transcripts(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    替换掉原先的 Mock 接口，直接从数据库读取真实分段
    """
    # 查询当前会议下所有的转录片段，按开始时间排序
    stmt = (
        select(TranscriptChunk)
        .where(TranscriptChunk.meeting_id == id)
        .order_by(TranscriptChunk.start.asc())
    )
    result = await db.execute(stmt)
    chunks = result.scalars().all()

    # 格式化输出
    return {
        "meeting_id": id,
        "total_chunks": len(chunks),
        "transcripts": [
            {
                "id": chunk.id,
                "start": chunk.start,
                "end": chunk.end,
                "speaker": chunk.speaker,
                "content": chunk.content
            }
            for chunk in chunks
        ]
    }

```

---

### 🔍 研发联调验证指引

1. **环境准备**：确认本地环境已执行 `pip install faster-whisper loguru`。
2. **测试上传**：使用 Postman 或 HTTP Client 向 `/api/meetings/upload` 发送一个 1 分钟左右的 `.mp3` 或 `.wav` 音频文件。
3. **观察日志**：检查控制台，应当看到 `Loading Faster-Whisper model...` -> `Detected language...` -> `Pipeline finished` 的持久化成功日志。
4. **前端刷新验证**：拿到接口返回的 `meeting_id`，请求 `GET /api/meetings/{id}/transcripts`。如果转录中，返回的 `transcripts` 数组为空；等几秒钟转录完成后再刷新，即可看到结构化的时间戳、Speaker 以及真实转录文字。前端原有的渲染逻辑无需修改即可无缝衔接。