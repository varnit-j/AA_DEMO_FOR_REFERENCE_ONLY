# Quick Reference: Database Management Commands

## 🚀 Quick Start

### One-Command Complete Migration
```bash
python database_manager.py full-setup
```
This does everything: backup current DB → export data → setup fresh DB → import data

---

## 📊 Most Common Tasks

### 1. Backup Current Database
```bash
python database_manager.py export
# Creates timestamped backup in data_exports/
```

### 2. Setup Fresh Database (Python 3.12)
```bash
python database_manager.py setup
# Complete setup: migrations + import
```

### 3. Import Data from CSV
```bash
python database_manager.py import --data ./path/to/csv/folder
```

### 4. Restore from Backup
```bash
python database_manager.py full-restore --backup-dir ./data_exports/export_YYYY-MM-DD_HH-MM-SS
```

---

## 🔧 Individual Tool Usage

### Export Only
```bash
# Export to default location (data_exports/)
python Data/export_db_to_csv.py

# Export to specific location
python Data/export_db_to_csv.py --output ./my_backup

# Export from custom database
python Data/export_db_to_csv.py --db ./custom/db.sqlite3 --output ./backup
```

### Setup Only
```bash
# Fresh setup with migrations and superuser
python setup_db_py312.py

# Setup without dependencies (already installed)
python setup_db_py312.py --skip-requirements

# Setup without auto-importing data
python setup_db_py312.py --skip-import
```

### Import Only
```bash
# Import from Data/ directory
python Data/import_all_from_csv.py

# Import from backup
python Data/import_all_from_csv.py --data ./my_backup
```

---

## 📁 CSV Files Generated

After export, you'll have these CSV files:

| File | Description |
|------|-------------|
| `airports.csv` | All airports/cities |
| `domestic_flights.csv` | Flight schedules & fares |
| `users.csv` | User accounts |
| `passengers.csv` | Passenger records |
| `tickets.csv` | Bookings |
| `orders.csv` | Orders (if orders app enabled) |
| `loyalty_tiers.csv` | Loyalty program tiers |
| `loyalty_accounts.csv` | User loyalty points |
| `bank_cards.csv` | Test bank cards |

---

## 🔐 Default Credentials After Setup

```
Username: admin
Password: admin123
```

⚠️ Change these in production!

---

## 📍 File Locations

```
Root/
├── database_manager.py         ← Master tool
├── setup_db_py312.py           ← Setup script
├── db.sqlite3                  ← Database
├── Data/
│   ├── export_db_to_csv.py     ← Export tool
│   ├── import_all_from_csv.py  ← Import tool
│   └── *.csv                   ← CSV data files
├── data_exports/               ← Generated exports
└── backups/                    ← Generated backups
```

---

## 🔄 Workflow Examples

### Complete Migration (Safe)
```bash
# Step 1: Backup current database
python database_manager.py export --output ./backup_2024_01_27

# Step 2: Setup fresh Python 3.12 environment
python database_manager.py setup --skip-import

# Step 3: Import backed-up data
python database_manager.py import --data ./backup_2024_01_27
```

### Full Automatic Workflow
```bash
python database_manager.py full-setup
```

### Restore from Existing Backup
```bash
python database_manager.py full-restore --backup-dir ./data_exports/export_2024-01-27_14-30-00
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Database already exists" | `rm db.sqlite3` before setup |
| "Django module not found" | Install requirements: `pip install -r requirements.txt` |
| "Python version mismatch" | Use Python 3.12: `python3.12 ...` |
| "Import fails" | Run setup first: `python database_manager.py setup` |
| "Import doesn't complete" | Check user exists: `python Data/import_all_from_csv.py` |

---

## ✅ Verification

After setup, verify database:

```bash
# Check database exists
ls -lh db.sqlite3

# Access Django shell
python manage.py shell

# Check records
python manage.py shell -c "from flight.models import Place; print(Place.objects.count())"
```

---

## 🌐 Access Application

After setup:

```bash
# Start server
python manage.py runserver

# Open browser
# Admin: http://localhost:8000/admin/
# App: http://localhost:8000/
```

---

**Version:** 1.0 | **Python:** 3.12+ | **Django:** 3.1+
