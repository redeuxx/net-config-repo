# net-config-repo

A full-stack network configuration management system. Supports HP ProCurve, Cisco IOS, and Aruba AOS-CX devices. Device type is auto-detected via SSH on add, or can be specified manually.

Additional vendors can be added in `backend/vendors/`.

## Running

**Development** (starts both servers in separate windows):

```powershell
./start-dev.ps1
```

Or manually:

```bash
# Backend — http://localhost:8000
cd backend
uv run uvicorn main:app --reload

# Frontend — http://localhost:5173
cd frontend
npm run dev
```

**Docker:**

```bash
docker-compose up
```

Frontend served at `http://localhost:80`, backend at `http://localhost:8000`.

## Web UI

The Vue 3 frontend provides the primary interface:

| Route            | Purpose                                    |
| ---------------- | ------------------------------------------ |
| `/`              | Dashboard — device counts, recent activity |
| `/devices`       | List, search, and manage devices           |
| `/devices/add`   | Add a device manually                      |
| `/devices/scan`  | Scan a CIDR range for devices              |
| `/devices/fetch` | Trigger a config fetch for all devices     |
| `/configs`       | Browse all config versions                 |
| `/logs`          | View application logs                      |

## CLI

```bash
cd backend
uv run python manage.py [OPTIONS]
```

| Option              | Description                                   |
| ------------------- | --------------------------------------------- |
| `--scan CIDR`       | Scan an IP or CIDR range for alive hosts      |
| `--list`            | List all devices in the database              |
| `--add IP`          | Add a device by IP (auto-detects type)        |
| `--remove ID`       | Remove a device by ID                         |
| `--fetchall`        | Fetch configs from all devices                |
| `--clean`           | Remove old configs from `running-configs/`    |
| `--search QUERY`    | Search devices by IP, hostname, or type       |
| `-add`              | Auto-add devices discovered during scan       |
| `-skip IPS`         | Comma-separated IPs to skip when using `-add` |
| `-device_type TYPE` | Manually specify device type when adding      |
| `-v, --version`     | Show version                                  |

## Stack

**Backend:** Python 3.11+, FastAPI, SQLAlchemy + Alembic (SQLite), Netmiko, icmplib, Uvicorn

**Frontend:** Vue 3, Vue Router, Vite, Tailwind CSS, Axios
