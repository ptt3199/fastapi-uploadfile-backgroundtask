from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from uuid import uuid4
import asyncio
import os
from os import path
import io
import time
import logging
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()
upload_tasks = {}

async def process_upload(file_content: bytes, filename: str, upload_id: str):
    total_size = len(file_content)
    chunk_size = 1024 * 1024  # 1MB chunks

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = path.join(settings.UPLOAD_DIR, f"{upload_id}_{filename}")
    
    try:
        with open(file_path, 'wb') as f:
            buffer = io.BytesIO(file_content)
            uploaded_size = 0
            start_time = time.time()
            last_update_time = start_time

            while True:
                if upload_tasks[upload_id]["status"] == "paused":
                    await asyncio.sleep(1)
                    start_time = time.time()  # Reset start time when resuming
                    continue
                elif upload_tasks[upload_id]["status"] == "canceled":
                    f.close()
                    os.remove(file_path)
                    logger.info(f"Upload {upload_id} canceled")
                    return

                chunk = buffer.read(chunk_size)
                if not chunk:
                    break

                f.write(chunk)
                uploaded_size += len(chunk)
                upload_tasks[upload_id]["uploaded_size"] = uploaded_size

                # Calculate and update current speed
                current_time = time.time()
                if current_time - last_update_time >= 1:  # Update speed every second
                    elapsed_time = current_time - start_time
                    current_speed = uploaded_size / elapsed_time if elapsed_time > 0 else 0
                    upload_tasks[upload_id]["current_speed"] = current_speed
                    last_update_time = current_time
                    logger.info(f"Upload {upload_id}: {uploaded_size}/{total_size} bytes, Speed: {current_speed:.2f} B/s")

                # Implement speed limiting
                target_speed = upload_tasks[upload_id]["speed"]
                elapsed_time = time.time() - start_time
                expected_time = uploaded_size / target_speed if target_speed > 0 else 0
                if elapsed_time < expected_time:
                    await asyncio.sleep(expected_time - elapsed_time)

        upload_tasks[upload_id]["status"] = "completed"
        logger.info(f"Upload {upload_id} completed")
    except Exception as e:
        logger.error(f"Error during upload {upload_id}: {str(e)}")
        upload_tasks[upload_id]["status"] = "failed"
        upload_tasks[upload_id]["error"] = str(e)

@router.post("/upload")
async def upload_file(
    file: UploadFile, 
    background_tasks: BackgroundTasks,
    speed: int = Query(settings.DEFAULT_UPLOAD_SPEED, description="Upload speed in bytes per second")
):
    upload_id = str(uuid4())
    file_content = await file.read()
    total_size = len(file_content)
    upload_tasks[upload_id] = {
        "status": "in_progress",
        "filename": file.filename,
        "uploaded_size": 0,
        "total_size": total_size,
        "speed": speed,
        "current_speed": 0
    }
    
    asyncio.create_task(process_upload(file_content, file.filename, upload_id))
    
    logger.info(f"Started upload {upload_id}: {file.filename}, Size: {total_size} bytes, Speed: {speed} B/s")
    return JSONResponse({
        "upload_id": upload_id, 
        "status": "started", 
        "total_size": total_size,
        "speed": speed
    })

@router.post("/upload/{upload_id}/pause")
async def pause_upload(upload_id: str):
    if upload_id not in upload_tasks:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    if upload_tasks[upload_id]["status"] == "in_progress":
        upload_tasks[upload_id]["status"] = "paused"
        logger.info(f"Upload {upload_id} paused")
        return JSONResponse({"status": "paused"})
    else:
        raise HTTPException(status_code=400, detail="Upload cannot be paused")

@router.post("/upload/{upload_id}/resume")
async def resume_upload(upload_id: str, speed: int = Query(None, description="New upload speed in bytes per second")):
    if upload_id not in upload_tasks:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    if upload_tasks[upload_id]["status"] == "paused":
        upload_tasks[upload_id]["status"] = "in_progress"
        if speed is not None:
            upload_tasks[upload_id]["speed"] = speed
        logger.info(f"Upload {upload_id} resumed with speed {upload_tasks[upload_id]['speed']} B/s")
        return JSONResponse({"status": "resumed", "speed": upload_tasks[upload_id]["speed"]})
    else:
        raise HTTPException(status_code=400, detail="Upload cannot be resumed")

@router.post("/upload/{upload_id}/cancel")
async def cancel_upload(upload_id: str):
    if upload_id not in upload_tasks:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    if upload_tasks[upload_id]["status"] in ["in_progress", "paused"]:
        upload_tasks[upload_id]["status"] = "canceled"
        logger.info(f"Upload {upload_id} canceled")
        return JSONResponse({"status": "canceled"})
    else:
        raise HTTPException(status_code=400, detail="Upload cannot be canceled")

@router.get("/upload/{upload_id}/status")
async def get_upload_status(upload_id: str):
    if upload_id not in upload_tasks:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    task = upload_tasks[upload_id]
    logger.info(f"Status request for upload {upload_id}: {task['status']}")
    return JSONResponse({
        "status": task["status"],
        "filename": task["filename"],
        "uploaded_size": task["uploaded_size"],
        "total_size": task["total_size"],
        "current_speed": task["current_speed"],
        "target_speed": task["speed"]
    })

@router.get("/uploads")
async def list_uploads():
    uploads_list = [
        {
            "upload_id": upload_id,
            "filename": task["filename"],
            "status": task["status"],
            "uploaded_size": task["uploaded_size"],
            "total_size": task["total_size"],
            "current_speed": task["current_speed"],
            "target_speed": task["speed"]
        }
        for upload_id, task in upload_tasks.items()
    ]
    logger.info(f"List uploads request: {len(uploads_list)} uploads")
    return JSONResponse({"uploads": uploads_list})