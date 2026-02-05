# Flight Booking System - Database Management README

## Overview

This package provides complete database management tools for the Flight Booking System, enabling:

✅ **Database Export** - Backup all data to CSV format  
✅ **Database Setup** - Create fresh database with Python 3.12  
✅ **Data Import** - Restore from CSV backups  
✅ **Full Workflow** - Complete migration in one command  
✅ **Disaster Recovery** - Restore from previous backups  

## What's Included

### Core Scripts

1. **`database_manager.py`** - Master orchestration tool
   - High-level commands for all database operations
   - Automatic backup creation
   - Workflow management

2. **`setup_db_py312.py`** - Python 3.12 Database Initialization
   - Django migration runner
   - Dependency installation
   - Superuser creation
   - Default configuration

3. **`Data/export_db_to_csv.py`** - Database Export Tool
   - Exports all tables to CSV format
   - Maintains data relationships
   - Supports custom output locations

4. **`Data/import_all_from_csv.py`** - Comprehensive Data Import
   - Imports from CSV using Django ORM
   - Handles relationships correctly
   - Supports partial imports
   - Optional app handling

### Documentation

- **`DATABASE_MIGRATION_GUIDE.md`** - Complete usage guide
- **`QUICK_REFERENCE.md`** - Quick lookup for common commands

## Quick Start

### Export Current Database
```bash
python database_manager.py export
```
Creates timestamped backup with all data in CSV format.

### Setup Python 3.12 Database
```bash
python database_manager.py setup
```
Complete setup with migrations and data import.

### Complete Migration (One Command)
```bash
python database_manager.py full-setup
```
Automatically handles: backup → export → setup → import

## System Requirements

- **Python:** 3.12 or higher
- **Django:** 3.1 or higher
- **SQLite3:** Built-in with Python
- **Disk Space:** Depends on data volume

## Installation

1. **Clone/download the project:**
   ```bash
   cd /path/to/AA_Flight_booking
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run initial setup:**
   ```bash
   python database_manager.py setup
   ```

## Usage Examples

### Basic Operations

```bash
# Export database to CSV
python database_manager.py export

# Setup fresh database
python database_manager.py setup

# Import from CSV
python database_manager.py import

# Complete workflow in one step
python database_manager.py full-setup
```

### Advanced Operations

```bash
# Export to specific location
python Data/export_db_to_csv.py --output ./my_backup

# Setup with specific database path
python setup_db_py312.py --db ./custom/db.sqlite3

# Import from specific backup
python database_manager.py import --data ./backups/export_2024-01-27

# Restore from backup
python database_manager.py full-restore --backup-dir ./backups/db_backup_2024-01-27
```

### Custom Paths

```bash
# All operations with custom paths
python database_manager.py setup --django-dir /path/to/project --db /path/to/db.sqlite3 --data /path/to/csvs
```

## CSV File Format

The export creates these CSV files:

```
airports.csv              - Places/Airports
domestic_flights.csv      - Flight schedules
users.csv                 - User accounts
passengers.csv            - Passenger records
tickets.csv               - Flight bookings
orders.csv                - Orders
loyalty_tiers.csv         - Loyalty program
loyalty_accounts.csv      - User loyalty points
bank_cards.csv            - Test bank cards
```

### Example: airports.csv
```
city,airport,code,country
Delhi,Indira Gandhi International Airport,DEL,India
Mumbai,Chhatrapati Shivaji International Airport,BOM,India
```

### Example: domestic_flights.csv
```
,origin,destination,depart_time,depart_weekday,duration,arrival_time,arrival_weekday,flight_no,airline_code,airline,economy_fare,business_fare,first_fare
0,DEL,BOM,08:00:00,2,02:10:00,10:10:00,2,G8334,G8,Go First,4589,,
```

## Default Credentials

After running setup, access the application with:

```
Username: admin
Password: admin123
```

**⚠️ Important:** Change these credentials immediately in production environments.

## Access Points

After setup, access the application at:

- **Admin Panel:** http://localhost:8000/admin/
- **Application:** http://localhost:8000/
- **API:** http://localhost:8000/api/

Start server with:
```bash
python manage.py runserver
```

## File Structure

```
AA_Flight_booking/
├── database_manager.py                 # Master tool
├── setup_db_py312.py                   # Setup script
├── DATABASE_MIGRATION_GUIDE.md          # Full documentation
├── QUICK_REFERENCE.md                  # Quick commands
├── db.sqlite3                          # SQLite database
├── manage.py                           # Django manage
├── requirements.txt                    # Dependencies
├── Data/
│   ├── export_db_to_csv.py             # Export tool
│   ├── import_all_from_csv.py          # Import tool
│   ├── import_flights_from_csv.py      # Original importer
│   ├── airports.csv                    # Airport data
│   ├── domestic_flights.csv            # Flight data
│   └── ...
├── flight/                             # Flight app
├── apps/
│   ├── orders/                         # Orders app
│   ├── loyalty/                        # Loyalty app
│   ├── banking/                        # Banking app
│   └── ...
└── capstone/                           # Django settings
```

## Common Tasks

### Backup for Safekeeping
```bash
python database_manager.py export --output ./monthly_backups/jan_2024
```

### Switch to Python 3.12
```bash
python3.12 database_manager.py setup
```

### Develop with Fresh Data
```bash
# Create backup first
python database_manager.py export

# Reset database
rm db.sqlite3

# Setup fresh
python database_manager.py setup
```

### Team Member Setup
```bash
# New team member clones repo and runs
python database_manager.py setup
# Done! Database ready with all data
```

### Test Environment Setup
```bash
# Export production data (for testing)
python database_manager.py export --output ./test_fixtures

# In test environment
python database_manager.py setup
python database_manager.py import --data ./test_fixtures
```

## Troubleshooting

### Database Already Exists
```bash
rm db.sqlite3
python database_manager.py setup
```

### Import Fails
```bash
# Check dependencies
pip install -r requirements.txt

# Run setup first
python database_manager.py setup

# Then import
python database_manager.py import
```

### Python Version Error
```bash
# Check version
python --version

# Use specific version
python3.12 database_manager.py setup
```

### Django Settings Error
```bash
# Ensure you're in project directory
cd /path/to/AA_Flight_booking

# Then run commands
python database_manager.py setup
```

### Lost Password
```bash
# Create new superuser
python manage.py createsuperuser
```

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| Export | 10-30s | Depends on data volume |
| Setup | 1-3 min | Includes migrations |
| Import | 1-5 min | Depends on CSV size |
| Full Workflow | 3-10 min | All steps combined |

## Backup Strategy

### Regular Backups
```bash
# Weekly backup
python database_manager.py export --output ./backups/weekly_$(date +%Y_%m_%d)
```

### Disaster Recovery
```bash
# Keep multiple backups
ls -la ./backups/

# Restore specific backup
python database_manager.py full-restore --backup-dir ./backups/export_2024-01-27_10-30-00
```

## Integration Examples

### Docker Deployment
```dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python setup_db_py312.py --skip-requirements
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Setup Database
  run: python database_manager.py setup --skip-requirements
- name: Run Tests
  run: python manage.py test
```

## Advanced Features

### Partial Import
```bash
# Import only essential data
python setup_db_py312.py --skip-import
python Data/import_all_from_csv.py --data ./places_only
```

### Custom Database Location
```bash
python database_manager.py setup --db /custom/location/db.sqlite3
```

### Separate Django Directory
```bash
python database_manager.py setup --django-dir /path/to/django/project
```

## Support

For issues or questions:

1. Check `DATABASE_MIGRATION_GUIDE.md` for detailed documentation
2. Review `QUICK_REFERENCE.md` for common commands
3. Check logs in terminal output
4. Verify all files are in correct locations
5. Ensure Python 3.12+ is installed

## Version Information

- **Script Version:** 1.0
- **Python:** 3.12+
- **Django:** 3.1+
- **SQLite:** Built-in
- **Last Updated:** January 2026

## License

Same as main Flight Booking System project.

---

**Ready to go!** Start with:
```bash
python database_manager.py setup
```
