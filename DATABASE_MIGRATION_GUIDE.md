# Database Migration & Setup Guide

## Overview

This guide explains how to use the database management tools to:
- Export your current database to CSV format
- Set up a fresh database with Python 3.12
- Import data from CSV files
- Create backups and restore from backups

## Files Created

### 1. **export_db_to_csv.py** - Database Export Tool
Exports all data from the SQLite database into CSV files.

**Location:** `Data/export_db_to_csv.py`

**Usage:**
```bash
# Export to current directory
python Data/export_db_to_csv.py

# Export to specific directory
python Data/export_db_to_csv.py --output ./backups/my_backup

# Export from specific database
python Data/export_db_to_csv.py --db mydb.sqlite3 --output ./backups
```

**Output Files:**
- `airports.csv` - All airport/place locations
- `domestic_flights.csv` - All flight information
- `users.csv` - User accounts
- `passengers.csv` - Passenger information
- `tickets.csv` - Flight tickets
- `orders.csv` - Orders (if orders app enabled)
- `loyalty_tiers.csv` - Loyalty tier definitions
- `loyalty_accounts.csv` - User loyalty accounts
- `bank_cards.csv` - Bank card data (if banking app enabled)

### 2. **setup_db_py312.py** - Python 3.12 Database Setup
Creates a fresh database with proper Django migrations and configuration.

**Location:** Root directory

**Usage:**
```bash
# Basic setup with defaults
python setup_db_py312.py

# Skip installing requirements (if already installed)
python setup_db_py312.py --skip-requirements

# Skip importing data (you can import later)
python setup_db_py312.py --skip-import

# Specify custom paths
python setup_db_py312.py --django-dir . --db mydb.sqlite3 --data ./Data
```

**Features:**
- Checks Python 3.12 compatibility
- Validates Django project structure
- Installs dependencies
- Runs migrations
- Creates default superuser (username: `admin`, password: `admin123`)
- Optionally imports CSV data

### 3. **import_all_from_csv.py** - Comprehensive Data Import
Imports all CSV data using Django ORM (handles relationships properly).

**Location:** `Data/import_all_from_csv.py`

**Usage:**
```bash
# Import from default location
python Data/import_all_from_csv.py

# Import from specific directory
python Data/import_all_from_csv.py --data ./my_data_backup
```

**Imports:**
- Places/Airports
- Flights with week relationships
- Users
- Passengers
- Loyalty tiers and accounts
- Bank cards

### 4. **database_manager.py** - Master Management Tool
Orchestrates the complete workflow with high-level commands.

**Location:** Root directory

**Usage:**

#### Export Current Database
```bash
# Export to auto-generated directory with timestamp
python database_manager.py export

# Export to specific directory
python database_manager.py export --output ./backups/2024-01-27
```

#### Setup Fresh Database
```bash
# Complete setup with migration and data import
python database_manager.py setup

# Setup without importing data
python database_manager.py setup --skip-import

# Setup without installing requirements
python database_manager.py setup --skip-requirements
```

#### Import Data
```bash
# Import from Data directory
python database_manager.py import

# Import from specific directory
python database_manager.py import --data ./my_backup
```

#### Complete Workflow: Export → Setup → Import
```bash
# Full migration with backup
python database_manager.py full-setup

# Full migration without creating backup
python database_manager.py full-setup --no-backup
```

#### Restore from Backup
```bash
# Restore from specific backup directory
python database_manager.py full-restore --backup-dir ./data_exports/export_2024-01-27_10-30-45
```

## Quick Start: Complete Database Migration

### Step 1: Export Current Database
```bash
python database_manager.py export --output ./my_backup
```
This creates CSV files of all current data.

### Step 2: Setup Python 3.12 Environment
```bash
# If using a fresh Python 3.12 environment
python database_manager.py setup --skip-import
```

### Step 3: Import Data
```bash
python database_manager.py import --data ./my_backup
```

Or use the complete workflow in one command:
```bash
python database_manager.py full-setup
```

## Advanced Usage

### Custom Database Path
```bash
python database_manager.py setup --db ./custom/path/db.sqlite3

python database_manager.py export --db ./custom/path/db.sqlite3 --output ./backup
```

### Separate Django Directory
```bash
python database_manager.py setup --django-dir /path/to/project --db /path/to/db.sqlite3
```

### Using Existing Data Backup
```bash
# If you have CSV files from a previous export
python database_manager.py setup
python database_manager.py import --data /path/to/exported/csvs
```

## CSV Format Specifications

### airports.csv
```
city,airport,code,country
Delhi,Indira Gandhi International Airport,DEL,India
Mumbai,Chhatrapati Shivaji International Airport,BOM,India
```

### domestic_flights.csv
```
,origin,destination,depart_time,depart_weekday,duration,arrival_time,arrival_weekday,flight_no,airline_code,airline,economy_fare,business_fare,first_fare
0,DEL,BOM,08:00:00,2,02:10:00,10:10:00,2,G8334,G8,Go First,4589,,
```

### users.csv
```
id,username,first_name,last_name,email,is_staff,is_active,date_joined
```

### tickets.csv
```
id,user_id,ref_no,flight_id,flight_ddate,flight_adate,flight_fare,other_charges,coupon_used,coupon_discount,total_fare,seat_class,booking_date,mobile,email,status,saga_correlation_id,failed_step
```

## Default Credentials

After setup, you can access the admin panel with:
- **Username:** `admin`
- **Password:** `admin123`

**Important:** Change these credentials in production!

## Troubleshooting

### Database Already Exists
```bash
# Remove old database before setup
rm db.sqlite3
python database_manager.py setup
```

### Import Fails Due to Missing Users
The import script handles missing foreign keys gracefully. Make sure:
1. Users are imported before tickets
2. Places/Airports are imported before flights
3. Loyalty tiers are imported before accounts

### Python Version Mismatch
```bash
# Check Python version
python --version

# Use Python 3.12 specifically
python3.12 database_manager.py setup
```

### Django Settings Module Not Found
```bash
# Make sure you're in the correct directory
cd /path/to/project
python database_manager.py setup
```

## File Locations

```
project/
├── database_manager.py           # Master tool
├── setup_db_py312.py             # Setup script
├── db.sqlite3                    # SQLite database
├── manage.py                     # Django manage script
├── Data/
│   ├── export_db_to_csv.py       # Export tool
│   ├── import_all_from_csv.py    # Import tool
│   ├── import_flights_from_csv.py # Original import tool
│   ├── airports.csv              # Place data
│   ├── domestic_flights.csv      # Flight data
│   └── ...
├── backups/                      # Auto-created during backup
│   └── db_backup_YYYY-MM-DD_HH-MM-SS/
└── data_exports/                 # Auto-created during export
    └── export_YYYY-MM-DD_HH-MM-SS/
```

## Performance Notes

### Export Performance
- Exports typically complete in seconds to minutes depending on data volume
- Each app module is exported independently

### Setup Performance
- Django migrations can take 1-2 minutes
- Dependency installation varies by network speed
- Database creation is instantaneous

### Import Performance
- CSV import uses Django ORM (slower than raw SQL)
- ~1000 records per second typical rate
- Flight import with week relationships is slower (multiple lookups)

## Backup and Recovery Strategy

### Regular Backups
```bash
# Create monthly backup
python database_manager.py export --output ./backups/monthly_2024_01
```

### Disaster Recovery
```bash
# If database corrupted
python database_manager.py full-setup --no-backup
# OR
python database_manager.py full-restore --backup-dir ./backups/db_backup_XXX
```

## Integration with CI/CD

### Automated Setup in Docker
```dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python setup_db_py312.py --skip-requirements
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Data Seeding in Tests
```bash
# Export production data
python database_manager.py export --output ./test_data

# Import in test environment
python database_manager.py import --data ./test_data
```

## Support and Issues

For issues with specific models or apps:
1. Check that all required apps are in `INSTALLED_APPS`
2. Verify migrations are applied: `python manage.py migrate --list`
3. Review Django logs for detailed error messages
4. Ensure CSV column names match the export format

---

**Version:** 1.0  
**Last Updated:** January 2026  
**Python Version:** 3.12+  
**Django Version:** 3.1+
