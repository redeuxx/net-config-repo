from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlalchemy.exc
from sqlalchemy.orm import Session

import db
import get_config
import get_hostname
import device as device_mod
import hosts
import utils

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Clean up any stuck "RUNNING" jobs from previous sessions
    db_session = db.SessionLocal()
    try:
        stuck_jobs = db_session.query(db.ScanJobs).filter_by(status="RUNNING").all()
        for job in stuck_jobs:
            job.status = "FAILED"
            job.message = "Scan interrupted (Server restarted)"
            job.completed_at = datetime.now()
        stuck_fetch_jobs = db_session.query(db.FetchJobs).filter_by(status="RUNNING").all()
        for job in stuck_fetch_jobs:
            job.status = "FAILED"
            job.message = "Fetch interrupted (Server restarted)"
            job.completed_at = datetime.now()
        db_session.commit()
    except Exception as e:
        print(f"Error cleaning up stuck jobs: {e}")
    finally:
        db_session.close()
    yield
    # Shutdown logic (if any) goes here

app = FastAPI(title="Net Config Repo API", version="1.0.0", lifespan=lifespan)

# Allow CORS for Vue frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class DeviceBase(BaseModel):
    ip: str
    hostname: str
    device_type: str

class DeviceCreate(BaseModel):
    ip: str
    username: Optional[str] = None
    password: Optional[str] = None
    enable_password: Optional[str] = None
    device_type: Optional[str] = None

class DeviceOut(DeviceBase):
    id: int
    class Config:
        from_attributes = True

class ConfigVersionOut(BaseModel):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

class ConfigDetailOut(ConfigVersionOut):
    config_text: str

class ConfigListOut(BaseModel):
    id: int
    device_id: int
    timestamp: datetime
    device_ip: str
    device_hostname: str
    class Config:
        from_attributes = True

class SettingsUpdate(BaseModel):
    max_configs_per_device: int
    default_username: Optional[str] = None
    default_password: Optional[str] = None
    default_enable_password: Optional[str] = None

class LogOut(BaseModel):
    id: int
    timestamp: datetime
    level: str
    message: str
    details: Optional[str] = None
    class Config:
        from_attributes = True

class ScanRequest(BaseModel):
    cidr: str

class ScanJobOut(BaseModel):
    id: int
    cidr: str
    status: str
    message: Optional[str] = None
    detailed_log: Optional[str] = None
    progress_current: int
    progress_total: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class FetchConfigsRequest(BaseModel):
    pass # Empty body for now

class FetchJobOut(BaseModel):
    id: int
    status: str
    message: Optional[str] = None
    detailed_log: Optional[str] = None
    progress_current: int
    progress_total: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    class Config:
        from_attributes = True

@app.get("/api/stats")
def get_stats(database: Session = Depends(db.get_db)):
    """Return summary statistics for the dashboard."""
    from sqlalchemy import func
    from datetime import timedelta

    total_devices = database.query(func.count(db.Devices.id)).scalar() or 0
    total_configs = database.query(func.count(db.ConfigVersions.id)).scalar() or 0

    since_24h = datetime.now() - timedelta(hours=24)
    configs_24h = database.query(func.count(db.ConfigVersions.id)).filter(
        db.ConfigVersions.timestamp >= since_24h
    ).scalar() or 0

    devices_with_configs_ids = database.query(db.ConfigVersions.device_id).distinct().subquery()
    devices_no_configs = database.query(func.count(db.Devices.id)).filter(
        ~db.Devices.id.in_(database.query(devices_with_configs_ids))
    ).scalar() or 0

    type_counts = database.query(
        db.Devices.device_type,
        func.count(db.Devices.id).label("count")
    ).group_by(db.Devices.device_type).order_by(func.count(db.Devices.id).desc()).all()

    last_fetch = database.query(db.FetchJobs).order_by(db.FetchJobs.id.desc()).first()
    last_scan = database.query(db.ScanJobs).order_by(db.ScanJobs.id.desc()).first()

    recent_configs = database.query(
        db.ConfigVersions.id,
        db.ConfigVersions.timestamp,
        db.Devices.ip,
        db.Devices.hostname,
        db.Devices.device_type,
    ).join(db.Devices).order_by(db.ConfigVersions.timestamp.desc()).limit(10).all()

    return {
        "total_devices": total_devices,
        "total_configs": total_configs,
        "configs_last_24h": configs_24h,
        "devices_without_configs": devices_no_configs,
        "device_type_breakdown": [{"type": t, "count": c} for t, c in type_counts],
        "last_fetch_job": {
            "status": last_fetch.status,
            "message": last_fetch.message,
            "started_at": last_fetch.started_at.isoformat(),
            "completed_at": last_fetch.completed_at.isoformat() if last_fetch.completed_at else None,
        } if last_fetch else None,
        "last_scan_job": {
            "status": last_scan.status,
            "cidr": last_scan.cidr,
            "message": last_scan.message,
            "started_at": last_scan.started_at.isoformat(),
            "completed_at": last_scan.completed_at.isoformat() if last_scan.completed_at else None,
        } if last_scan else None,
        "recent_configs": [
            {
                "id": r.id,
                "timestamp": r.timestamp.isoformat(),
                "ip": r.ip,
                "hostname": r.hostname,
                "device_type": r.device_type,
            }
            for r in recent_configs
        ],
    }

@app.get("/api/devices", response_model=List[DeviceOut])
def list_devices(database: Session = Depends(db.get_db)):
    """List all devices in the database."""
    devices = database.query(db.Devices).all()
    return devices

@app.get("/api/devices/search", response_model=List[DeviceOut])
def search_devices(query: str, database: Session = Depends(db.get_db)):
    """Search for a device."""
    from sqlalchemy import or_
    devices = database.query(db.Devices).filter(
        or_(
            db.Devices.ip.like(f"%{query}%"),
            db.Devices.hostname.like(f"%{query}%"),
            db.Devices.device_type.like(f"%{query}%"),
        )
    ).all()
    return devices

@app.post("/api/devices", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_device(device_req: DeviceCreate, database: Session = Depends(db.get_db)):
    """Add a new device to the database."""
    if db.is_device_in_db(device_req.ip):
        raise HTTPException(status_code=400, detail="Device already exists")

    if not hosts.is_alive(device_req.ip):
        raise HTTPException(status_code=400, detail="Device is not reachable")

    credentials = utils.get_credentials(database)
    username = device_req.username or credentials["username"]
    password = device_req.password or credentials["password"]
    enable_password = device_req.enable_password or credentials["enable_password"]

    if not enable_password:
        enable_password = password

    device_type = device_req.device_type
    if not device_type:
        device_type = device_mod.detect_device(device_req.ip, username, password, enable_password)

    if device_type:
        hostname = get_hostname.get_hostname(device_req.ip, device_type, username, password, enable_password)
        success = db.insert_device(device_req.ip, hostname, device_type, username, password, enable_password)
        if success:
            return {"message": f"Device {device_req.ip} added successfully."}
        else:
            raise HTTPException(status_code=400, detail="Device already exists")
    else:
        raise HTTPException(status_code=400, detail="Could not connect or detect device type")

@app.delete("/api/devices/{device_id}")
def delete_device(device_id: int, database: Session = Depends(db.get_db)):
    """Remove a device from the database."""
    success = db.remove_device(device_id)
    if success:
        return {"message": "Device removed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Device not found")

# --- Config Endpoints ---

@app.get("/api/devices/{device_id}/configs", response_model=List[ConfigVersionOut])
def get_device_configs(device_id: int, database: Session = Depends(db.get_db)):
    """List config versions for a device."""
    configs = database.query(db.ConfigVersions).filter_by(device_id=device_id).order_by(db.ConfigVersions.timestamp.desc()).all()
    return configs

@app.get("/api/configs/{config_id}", response_model=ConfigDetailOut)
def get_config_detail(config_id: int, database: Session = Depends(db.get_db)):
    """Get full details of a specific config."""
    config = database.query(db.ConfigVersions).filter_by(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config

@app.get("/api/configs", response_model=List[ConfigListOut])
def list_all_configs(database: Session = Depends(db.get_db)):
    """List all configuration versions globally."""
    results = database.query(
        db.ConfigVersions.id,
        db.ConfigVersions.device_id,
        db.ConfigVersions.timestamp,
        db.Devices.ip.label("device_ip"),
        db.Devices.hostname.label("device_hostname")
    ).join(db.Devices).order_by(db.ConfigVersions.timestamp.desc()).limit(200).all()
    return results

@app.get("/api/configs/{config_id}/download", response_class=PlainTextResponse)
def download_config(config_id: int, database: Session = Depends(db.get_db)):
    """Download a config as a text file."""
    config = database.query(db.ConfigVersions).filter_by(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    device = database.query(db.Devices).filter_by(id=config.device_id).first()
    timestamp_str = config.timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp_str}_{device.ip}.txt"
    
    return PlainTextResponse(
        content=config.config_text,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# --- Settings & Logs Endpoints ---

@app.get("/api/settings", response_model=SettingsUpdate)
def get_settings(database: Session = Depends(db.get_db)):
    """Get global settings."""
    def get_val(key, default=""):
        setting = database.query(db.Settings).filter_by(key=key).first()
        return setting.value if setting else default

    return {
        "max_configs_per_device": int(get_val("max_configs_per_device", 10)),
        "default_username": get_val("default_username", ""),
        "default_password": get_val("default_password", ""),
        "default_enable_password": get_val("default_enable_password", "")
    }

@app.post("/api/settings")
def update_settings(settings: SettingsUpdate, database: Session = Depends(db.get_db)):
    """Update global settings."""
    def set_val(key, val):
        setting = database.query(db.Settings).filter_by(key=key).first()
        if setting:
            setting.value = str(val) if val is not None else ""
        else:
            database.add(db.Settings(key=key, value=str(val) if val is not None else ""))

    set_val("max_configs_per_device", settings.max_configs_per_device)
    set_val("default_username", settings.default_username)
    set_val("default_password", settings.default_password)
    set_val("default_enable_password", settings.default_enable_password)
    database.commit()
    return {"message": "Settings updated"}

@app.get("/api/logs", response_model=List[LogOut])
def get_logs(database: Session = Depends(db.get_db)):
    """Get the latest 100 application logs."""
    logs = database.query(db.Logs).order_by(db.Logs.id.desc()).limit(100).all()
    return logs

@app.get("/api/jobs/scan", response_model=List[ScanJobOut])
def get_scan_jobs(database: Session = Depends(db.get_db)):
    """Get the latest 5 scan jobs."""
    jobs = database.query(db.ScanJobs).order_by(db.ScanJobs.id.desc()).limit(5).all()
    return jobs

# --- Background task functions ---

def task_fetch_configs(job_id: int):
    """Background task to fetch configs for all devices with job tracking."""
    db_session = db.SessionLocal()
    job = db_session.query(db.FetchJobs).filter_by(id=job_id).first()
    if not job:
        db_session.close()
        return

    def ts():
        return datetime.now().strftime("%H:%M:%S")

    def log_job(msg):
        line = f"[{ts()}] {msg}"
        job.message = msg
        job.detailed_log = (job.detailed_log or "") + line + "\n"
        db_session.commit()

    try:
        devices = db_session.query(db.Devices).all()
        job.progress_total = len(devices)
        db_session.commit()

        if not devices:
            log_job("No devices in database.")
            job.status = "COMPLETED"
            job.completed_at = datetime.now()
            db_session.commit()
            return

        device_dicts = [
            {
                "id": d.id, "ip": d.ip, "device_type": d.device_type,
                "username": d.username, "password": d.password,
                "enable_password": d.enable_password,
            }
            for d in devices if d.ip and d.device_type
        ]
        skipped = len(devices) - len(device_dicts)
        if skipped:
            log_job(f"Skipping {skipped} device(s) with missing IP or device type.")
        job.progress_total = len(device_dicts)
        db_session.commit()

        if not device_dicts:
            log_job("No valid devices to fetch.")
            job.status = "COMPLETED"
            job.completed_at = datetime.now()
            db_session.commit()
            return

        log_job(f"Starting config fetch for {len(device_dicts)} device(s)...")

        ATTEMPT_TIMEOUT = 45  # seconds before giving up on a single attempt

        def try_get_config(device):
            """Run get_config in a daemon thread with periodic status updates and a hard timeout.
            Uses threading.Event instead of ThreadPoolExecutor to avoid shutdown(wait=True) blocking."""
            label = f"{device['ip']} ({device['device_type']})"
            result_holder = [None]
            done_event = threading.Event()

            def run():
                result_holder[0] = get_config.get_config(
                    device['username'], device['password'], device['ip'],
                    device['device_type'], device['enable_password'],
                )
                done_event.set()

            t = threading.Thread(target=run, daemon=True)
            t.start()

            elapsed = 0
            poll = 5
            while not done_event.wait(timeout=poll):
                elapsed += poll
                if elapsed >= ATTEMPT_TIMEOUT:
                    log_job(f"[{label}] No response after {elapsed}s — aborting attempt.")
                    return f"Error: Timed out after {elapsed}s with no response"
                log_job(f"[{label}] Still waiting... ({elapsed}s elapsed)")

            return result_holder[0]

        for device in device_dicts:
            label = f"{device['ip']} ({device['device_type']})"
            log_job(f"[{label}] Starting... ({device_dicts.index(device) + 1}/{len(device_dicts)})")
            config = "Error: Connection failed"
            t_start = time.monotonic()
            for attempt in range(11):
                log_job(f"[{label}] Attempt {attempt + 1}/11 — connecting...")
                config = try_get_config(device)
                if "Error:" not in config:
                    elapsed = time.monotonic() - t_start
                    log_job(f"[{label}] SUCCESS — {len(config)} bytes in {elapsed:.1f}s.")
                    break
                error_detail = config.split("\n", 1)[-1].strip() if "\n" in config else config
                log_job(f"[{label}] Attempt {attempt + 1}/11 failed: {error_detail}")
                if attempt < 10:
                    log_job(f"[{label}] Waiting 1s before retry {attempt + 2}/11...")
                    time.sleep(1)

            job.progress_current += 1
            if "Error:" not in config:
                new_config = db.ConfigVersions(device_id=device['id'], config_text=config.strip())
                db_session.add(new_config)
                log_job(f"[{label}] Config saved to database.")
            else:
                error_detail = config.split("\n", 1)[-1].strip() if "\n" in config else config
                utils.log_message(db_session, "ERROR", f"Config fetch failed for {device['ip']}", config.strip())
                log_job(f"[{label}] FAILED after 11 attempts. Last error: {error_detail}")
            db_session.commit()

        utils.del_oldest_configs(db_session=db_session)
        log_job("All devices processed. Old configs pruned.")
        job.status = "COMPLETED"
        job.message = "Fetch finished successfully."
        job.completed_at = datetime.now()
        db_session.commit()

    except Exception as e:
        utils.log_message(db_session, "ERROR", "Config fetch job failed", str(e))
        job.status = "FAILED"
        job.message = f"Error: {str(e)}"
        job.detailed_log = (job.detailed_log or "") + f"[{ts()}] ERROR: {str(e)}\n"
        job.completed_at = datetime.now()
        db_session.commit()
    finally:
        db_session.close()

import concurrent.futures
import threading
import time

def task_scan_cidr(job_id: int, cidr: str):
    """Background task to scan a CIDR block and add devices."""
    db_session = db.SessionLocal()
    job = db_session.query(db.ScanJobs).filter_by(id=job_id).first()
    
    if not job:
        db_session.close()
        return

    db_lock = threading.Lock()

    def log_job(msg):
        with db_lock:
            job.message = msg
            job.detailed_log = (job.detailed_log or "") + msg + "\n"
            db_session.commit()

    try:
        log_job(f"Starting scan for {cidr}...")

        credentials = utils.get_credentials(db_session)
        username = credentials["username"]
        password = credentials["password"]
        enable_password = credentials["enable_password"]
        if enable_password == "":
            enable_password = password

        alive_hosts = hosts.scan_cidr(cidr, print_fn=log_job)
        alive_hosts_final = []

        for device_ip in alive_hosts:
            if not db.is_device_in_db(device_ip):
                alive_hosts_final.append(device_ip)

        with db_lock:
            job.progress_total = len(alive_hosts_final)
            if job.progress_total == 0:
                job.message = "No new alive hosts found."
                job.status = "COMPLETED"
                job.completed_at = datetime.now()
                db_session.commit()
                return
            db_session.commit()

        devices_object = []

        def process_host(device_ip):
            log_job(f"Detecting device type for {device_ip}...")
            with db_lock:
                job.progress_current += 1
                db_session.commit()

            device_type = None
            # Initial attempt + 10 retries
            for attempt in range(11):
                device_type = device_mod.detect_device(device_ip, username, password, enable_password)
                if device_type:
                    break
                if attempt < 10:
                    log_job(f"Attempt {attempt + 1}/11 failed for {device_ip}. Retrying...")
                    time.sleep(1)

            if device_type:
                log_job(f"Successfully detected {device_ip} as {device_type}. Getting hostname...")
                hostname = get_hostname.get_hostname(device_ip, device_type, username, password, enable_password)
                log_job(f"Hostname for {device_ip} is {hostname}.")
                class Item:
                    pass
                item = Item()
                item.ip = device_ip
                item.hostname = hostname
                item.device_type = device_type
                item.username = username
                item.password = password
                item.enable_password = enable_password
                
                with db_lock:
                    devices_object.append(item)
            else:
                log_job(f"Failed to connect or detect device type for {device_ip} after 11 attempts.")
                with db_lock:
                    utils.log_message(db_session, "ERROR", f"Device detection failed for {device_ip}", "All 11 retry attempts exhausted.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(process_host, alive_hosts_final)

        if devices_object:
            log_job(f"Saving {len(devices_object)} devices to database...")
            with db_lock:
                db.insert_device_bulk(devices_object)
        
        with db_lock:
            job.status = "COMPLETED"
            job.message = "Scan finished successfully."
            job.detailed_log = (job.detailed_log or "") + "Scan finished successfully.\n"
            job.completed_at = datetime.now()
            db_session.commit()

    except Exception as e:
        utils.log_message(db_session, "ERROR", f"Scan job {job_id} failed on {cidr}", str(e))
        with db_lock:
            job.status = "FAILED"
            job.message = f"Error: {str(e)}"
            job.detailed_log = (job.detailed_log or "") + f"Error: {str(e)}\n"
            job.completed_at = datetime.now()
            db_session.commit()
    finally:
        db_session.close()


@app.get("/api/jobs/fetch", response_model=List[FetchJobOut])
def get_fetch_jobs(database: Session = Depends(db.get_db)):
    """Get the latest 5 fetch jobs."""
    jobs = database.query(db.FetchJobs).order_by(db.FetchJobs.id.desc()).limit(5).all()
    return jobs

def task_fetch_single_device(job_id: int, device_id: int):
    """Background task to fetch config for a single device with job tracking."""
    db_session = db.SessionLocal()
    job = db_session.query(db.FetchJobs).filter_by(id=job_id).first()
    if not job:
        db_session.close()
        return

    def ts():
        return datetime.now().strftime("%H:%M:%S")

    def log_job(msg):
        line = f"[{ts()}] {msg}"
        job.message = msg
        job.detailed_log = (job.detailed_log or "") + line + "\n"
        db_session.commit()

    try:
        device = db_session.query(db.Devices).filter_by(id=device_id).first()
        if not device:
            job.status = "FAILED"
            job.message = "Device not found."
            job.completed_at = datetime.now()
            db_session.commit()
            return

        if not device.ip or not device.device_type:
            job.status = "FAILED"
            job.message = "Device has missing IP or device type."
            job.completed_at = datetime.now()
            db_session.commit()
            return

        device_dict = {
            "id": device.id, "ip": device.ip, "device_type": device.device_type,
            "username": device.username, "password": device.password,
            "enable_password": device.enable_password,
        }
        job.progress_total = 1
        db_session.commit()

        label = f"{device_dict['ip']} ({device_dict['device_type']})"
        ATTEMPT_TIMEOUT = 45

        def try_get_config(device):
            result_holder = [None]
            done_event = threading.Event()
            def run():
                result_holder[0] = get_config.get_config(
                    device['username'], device['password'], device['ip'],
                    device['device_type'], device['enable_password'],
                )
                done_event.set()
            t = threading.Thread(target=run, daemon=True)
            t.start()
            elapsed = 0
            poll = 5
            while not done_event.wait(timeout=poll):
                elapsed += poll
                if elapsed >= ATTEMPT_TIMEOUT:
                    log_job(f"[{label}] No response after {elapsed}s — aborting attempt.")
                    return f"Error: Timed out after {elapsed}s with no response"
                log_job(f"[{label}] Still waiting... ({elapsed}s elapsed)")
            return result_holder[0]

        log_job(f"[{label}] Starting fetch...")
        config = "Error: Connection failed"
        t_start = time.monotonic()
        for attempt in range(11):
            log_job(f"[{label}] Attempt {attempt + 1}/11 — connecting...")
            config = try_get_config(device_dict)
            if "Error:" not in config:
                elapsed = time.monotonic() - t_start
                log_job(f"[{label}] SUCCESS — {len(config)} bytes in {elapsed:.1f}s.")
                break
            error_detail = config.split("\n", 1)[-1].strip() if "\n" in config else config
            log_job(f"[{label}] Attempt {attempt + 1}/11 failed: {error_detail}")
            if attempt < 10:
                log_job(f"[{label}] Waiting 1s before retry {attempt + 2}/11...")
                time.sleep(1)

        job.progress_current = 1
        if "Error:" not in config:
            new_config = db.ConfigVersions(device_id=device_dict['id'], config_text=config.strip())
            db_session.add(new_config)
            utils.del_oldest_configs(db_session=db_session)
            log_job(f"[{label}] Config saved to database.")
            job.status = "COMPLETED"
            job.message = f"Config fetched successfully for {device_dict['ip']}."
        else:
            error_detail = config.split("\n", 1)[-1].strip() if "\n" in config else config
            utils.log_message(db_session, "ERROR", f"Config fetch failed for {device_dict['ip']}", config.strip())
            log_job(f"[{label}] FAILED after 11 attempts. Last error: {error_detail}")
            job.status = "FAILED"
            job.message = f"Failed to fetch config for {device_dict['ip']}."

        job.completed_at = datetime.now()
        db_session.commit()

    except Exception as e:
        utils.log_message(db_session, "ERROR", "Single device config fetch failed", str(e))
        job.status = "FAILED"
        job.message = f"Error: {str(e)}"
        job.detailed_log = (job.detailed_log or "") + f"[{ts()}] ERROR: {str(e)}\n"
        job.completed_at = datetime.now()
        db_session.commit()
    finally:
        db_session.close()


@app.get("/api/jobs/fetch/{job_id}", response_model=FetchJobOut)
def get_fetch_job(job_id: int, database: Session = Depends(db.get_db)):
    """Get the status of a specific fetch job."""
    job = database.query(db.FetchJobs).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/api/jobs/fetch")
def trigger_fetch_configs(background_tasks: BackgroundTasks, database: Session = Depends(db.get_db)):
    """Trigger background job to fetch configs for all devices."""
    new_job = db.FetchJobs(status="RUNNING", message="Starting...")
    database.add(new_job)
    database.commit()
    database.refresh(new_job)
    background_tasks.add_task(task_fetch_configs, new_job.id)
    return {"message": "Config fetch job started in the background"}

@app.post("/api/devices/{device_id}/fetch")
def trigger_device_fetch(device_id: int, background_tasks: BackgroundTasks, database: Session = Depends(db.get_db)):
    """Trigger a background job to fetch config for a single device."""
    device = database.query(db.Devices).filter_by(id=device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    new_job = db.FetchJobs(status="RUNNING", message=f"Starting fetch for {device.ip}...")
    database.add(new_job)
    database.commit()
    database.refresh(new_job)
    background_tasks.add_task(task_fetch_single_device, new_job.id, device_id)
    return {"job_id": new_job.id, "message": f"Config fetch started for {device.ip}"}

@app.post("/api/jobs/scan")
def trigger_scan(scan_req: ScanRequest, background_tasks: BackgroundTasks, database: Session = Depends(db.get_db)):
    """Trigger background job to scan a CIDR block."""
    new_job = db.ScanJobs(cidr=scan_req.cidr, status="RUNNING", message="Starting scan...")
    database.add(new_job)
    database.commit()
    database.refresh(new_job)

    background_tasks.add_task(task_scan_cidr, new_job.id, scan_req.cidr)
    return {"message": f"Scan job for {scan_req.cidr} started in the background"}
