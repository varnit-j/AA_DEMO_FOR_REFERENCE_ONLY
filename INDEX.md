# Database Management System - Index & Getting Started

## 📍 You Are Here

This folder contains a complete database management system for the Flight Booking application.

## 🚀 Get Started in 3 Steps

### Step 1: Choose Your Platform
```bash
# Windows
database_manager.bat full-setup

# Linux/Mac
bash database_manager.sh full-setup

# Or directly
python database_manager.py full-setup
```

### Step 2: Wait for Completion
The script will:
- ✅ Create backups
- ✅ Export data to CSV
- ✅ Set up fresh database
- ✅ Import all data
- ✅ Create admin account

### Step 3: Access Application
```bash
python manage.py runserver
```
Then visit: `http://localhost:8000/admin/`

Login: `admin` / `admin123`

---

## 📚 Documentation

### For Quick Commands
👉 **Start here:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- Common commands
- Quick examples
- File locations
- Troubleshooting

### For Complete Guide
👉 **Read this:** [DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md)
- Detailed instructions
- CSV formats
- Advanced usage
- CI/CD integration

### For Overview
👉 **See this:** [DATABASE_TOOLS_README.md](DATABASE_TOOLS_README.md)
- What's included
- System requirements
- Usage examples
- Common tasks

### For Implementation Details
👉 **Check this:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- What was created
- How to use it
- File structure
- Testing checklist

---

## 🔧 Main Tools

### 1. Master Tool: `database_manager.py`
**High-level orchestration**

```bash
python database_manager.py full-setup      # Complete workflow
python database_manager.py export          # Backup data
python database_manager.py setup           # Fresh database
python database_manager.py import          # Restore data
```

### 2. Export Tool: `Data/export_db_to_csv.py`
**Export database to CSV**

```bash
python Data/export_db_to_csv.py
python Data/export_db_to_csv.py --output ./my_backup
```

### 3. Setup Tool: `setup_db_py312.py`
**Initialize Python 3.12 database**

```bash
python setup_db_py312.py
python setup_db_py312.py --skip-import
```

### 4. Import Tool: `Data/import_all_from_csv.py`
**Import CSV to database**

```bash
python Data/import_all_from_csv.py
python Data/import_all_from_csv.py --data ./backup
```

---

## 💾 CSV Files

The system works with these CSV files:

| File | Purpose | Created By |
|------|---------|-----------|
| `airports.csv` | Airport/place locations | Export tool |
| `domestic_flights.csv` | Flight schedules | Export tool |
| `users.csv` | User accounts | Export tool |
| `passengers.csv` | Passenger records | Export tool |
| `tickets.csv` | Flight bookings | Export tool |
| `orders.csv` | Orders (optional) | Export tool |
| `loyalty_tiers.csv` | Loyalty tiers | Export tool |
| `loyalty_accounts.csv` | User loyalty data | Export tool |
| `bank_cards.csv` | Test bank cards | Export tool |

---

## 📊 Quick Command Reference

### Most Common Commands

```bash
# Complete setup (recommended)
python database_manager.py full-setup

# Just export current data
python database_manager.py export

# Just setup fresh database
python database_manager.py setup

# Just import from backup
python database_manager.py import

# Restore from specific backup
python database_manager.py full-restore --backup-dir ./backup_dir
```

### With Options

```bash
# Export to specific location
python database_manager.py export --output ./my_backup

# Setup without installing deps
python database_manager.py setup --skip-requirements

# Setup without auto-importing
python database_manager.py setup --skip-import

# Custom database path
python database_manager.py setup --db ./custom/db.sqlite3

# Custom Django directory
python database_manager.py setup --django-dir /path/to/project
```

---

## 🏗️ File Structure

```
📁 AA_Flight_booking/
│
├── 🎯 database_manager.py              ← START HERE
├── 🎯 database_manager.bat             ← For Windows
├── 🎯 database_manager.sh              ← For Linux/Mac
│
├── 🔧 setup_db_py312.py                ← Database setup
│
├── 📖 QUICK_REFERENCE.md               ← Quick commands
├── 📖 DATABASE_MIGRATION_GUIDE.md       ← Full guide
├── 📖 DATABASE_TOOLS_README.md          ← Complete README
├── 📖 IMPLEMENTATION_SUMMARY.md         ← What was created
├── 📖 INDEX.md                         ← This file
│
├── 📁 Data/
│   ├── export_db_to_csv.py             ← Export tool
│   ├── import_all_from_csv.py          ← Import tool
│   ├── import_flights_from_csv.py      ← Original importer
│   ├── airports.csv                    ← Airport data
│   ├── domestic_flights.csv            ← Flight data
│   └── ... (other CSVs)
│
├── 📁 data_exports/                    ← Generated exports
├── 📁 backups/                         ← Generated backups
│
└── 🗄️  db.sqlite3                       ← SQLite database
```

---

## ⚡ Quick Workflows

### Workflow 1: First Time Setup
```bash
# Complete automatic setup
python database_manager.py setup
```

### Workflow 2: Backup Before Changes
```bash
# Export current data
python database_manager.py export --output ./backup_before_changes
```

### Workflow 3: Reset to Fresh State
```bash
# Complete reset with backup
python database_manager.py full-setup
```

### Workflow 4: Restore from Backup
```bash
# Find your backup directory
ls backups/

# Restore it
python database_manager.py full-restore --backup-dir ./backups/db_backup_XXX
```

### Workflow 5: Team Member Onboarding
New developer just runs:
```bash
python database_manager.py setup
```
Done! Database ready with all data.

---

## 🔐 Default Access

After setup, login with:
```
Username: admin
Password: admin123
```

⚠️ **Change these in production!**

To create new superuser:
```bash
python manage.py createsuperuser
```

---

## 📋 Checklist: First Run

- [ ] Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- [ ] Run: `python database_manager.py setup`
- [ ] Start server: `python manage.py runserver`
- [ ] Visit: http://localhost:8000/admin/
- [ ] Login with admin/admin123
- [ ] Verify data is there
- [ ] Change admin password
- [ ] Bookmark [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 🔍 Verify Installation

Check that everything works:

```bash
# Check Python
python --version
# Should be 3.12+

# Check Django
python manage.py --version
# Should be 3.1+

# Check database exists
ls -lh db.sqlite3

# Check migration status
python manage.py migrate --list

# Run tests (optional)
python manage.py test
```

---

## 🆘 Common Issues

### "Database already exists"
```bash
rm db.sqlite3
python database_manager.py setup
```

### "Python not found"
```bash
# Install Python 3.12 or use Python 3.12 directly
python3.12 database_manager.py setup
```

### "Django module not found"
```bash
pip install -r requirements.txt
python database_manager.py setup
```

### "Permission denied"
```bash
# Make scripts executable
chmod +x database_manager.sh database_manager.bat
```

For more help, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md#-troubleshooting) troubleshooting section.

---

## 📞 Where to Go For Help

| Question | Where to Look |
|----------|---------------|
| How do I...? | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| How does it work? | [DATABASE_TOOLS_README.md](DATABASE_TOOLS_README.md) |
| Detailed guide? | [DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md) |
| What was created? | [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) |
| Specific tool help? | `python script.py --help` |

---

## 📈 Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| Full setup | 3-10 min | First time is slower |
| Export | 10-30 sec | Depends on data |
| Import | 1-5 min | Using Django ORM |
| Just migrations | 30-60 sec | No data import |

---

## ✅ Next Steps

### Immediate
1. Run: `python database_manager.py setup`
2. Start server: `python manage.py runserver`
3. Access: http://localhost:8000/admin/

### Soon
1. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. Explore the admin panel
3. Check the flight data

### Later
1. Read [DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md)
2. Set up regular backups
3. Integrate into CI/CD if needed

---

## 💡 Pro Tips

✨ **Use shell scripts** for convenience:
```bash
# Windows
database_manager.bat setup

# Linux/Mac
bash database_manager.sh setup
```

✨ **Create regular backups:**
```bash
python database_manager.py export --output ./backup_$(date +%Y_%m_%d)
```

✨ **Automate team setup:**
```bash
# New team member's first command
python database_manager.py setup
```

✨ **CI/CD integration:**
```yaml
- run: python database_manager.py setup --skip-requirements
```

---

## 📌 Key Files to Remember

- **Master Tool:** `database_manager.py`
- **Quick Help:** `QUICK_REFERENCE.md`
- **Full Guide:** `DATABASE_MIGRATION_GUIDE.md`
- **Database:** `db.sqlite3`
- **CSVs:** `Data/` folder

---

## 🎉 You're All Set!

Everything is ready. Start with:

```bash
python database_manager.py setup
```

Then visit: http://localhost:8000/admin/

---

**Version:** 1.0  
**Updated:** January 2026  
**Python:** 3.12+  
**Status:** Ready to use ✅
