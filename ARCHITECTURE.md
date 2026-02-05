# System Architecture & Data Flow

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Database Management System                    │
│                   Flight Booking Application                     │
└─────────────────────────────────────────────────────────────────┘

                         ┌──────────────────┐
                         │ database_manager │
                         │  Master Tool     │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌──────────────┐ ┌──────────┐ ┌──────────┐
            │   Export     │ │  Setup   │ │ Import   │
            │   Tool       │ │  Tool    │ │  Tool    │
            └──────┬───────┘ └────┬─────┘ └────┬─────┘
                   │              │            │
         ┌─────────▼────┐    ┌────▼─────┐    ▼──────────┐
         │  CSV Files   │    │ Django   │   CSV Files  │
         │              │    │ Migrations   (Input)    │
         │ • airports   │    │ + Superuser             │
         │ • flights    │    │ + Config                │
         │ • users      │    └──────────┘              │
         │ • etc        │                              │
         └──────────────┘                              │
                                                       │
                              ┌────────────────────────┘
                              │
                              ▼
                         ┌──────────────┐
                         │   Database   │
                         │ db.sqlite3   │
                         └──────────────┘
```

---

## 📊 Data Flow Diagram

### Export Flow
```
Current Database (db.sqlite3)
          ▼
    ┌─────────────────────────────┐
    │  export_db_to_csv.py        │
    │  ├─ Read Places             │
    │  ├─ Read Flights            │
    │  ├─ Read Users              │
    │  ├─ Read Passengers         │
    │  ├─ Read Tickets            │
    │  ├─ Read Orders (optional)  │
    │  ├─ Read Loyalty (optional) │
    │  └─ Read Banking (optional) │
    └─────────────────────────────┘
          ▼
    ┌─────────────────────────────┐
    │   CSV Files                 │
    │   ├─ airports.csv           │
    │   ├─ domestic_flights.csv   │
    │   ├─ users.csv              │
    │   ├─ passengers.csv         │
    │   ├─ tickets.csv            │
    │   ├─ orders.csv             │
    │   ├─ loyalty_tiers.csv      │
    │   ├─ loyalty_accounts.csv   │
    │   └─ bank_cards.csv         │
    └─────────────────────────────┘
          ▼
    Backup / Portable Format
```

### Setup Flow
```
Empty Environment (Python 3.12)
          ▼
    ┌─────────────────────────────┐
    │  setup_db_py312.py          │
    │  ├─ Check Python Version    │
    │  ├─ Validate Django         │
    │  ├─ Install Requirements    │
    │  ├─ Run Migrations          │
    │  ├─ Create Superuser        │
    │  └─ Create Fresh db.sqlite3 │
    └─────────────────────────────┘
          ▼
    ┌─────────────────────────────┐
    │   Fresh Database            │
    │   ├─ All tables created     │
    │   ├─ Schema ready           │
    │   └─ Ready for data         │
    └─────────────────────────────┘
          ▼
    Ready for Application / Data Import
```

### Import Flow
```
CSV Files (CSV Format)
          ▼
    ┌─────────────────────────────┐
    │  import_all_from_csv.py     │
    │  ├─ Import Places           │
    │  ├─ Import Flights          │
    │  ├─ Import Users            │
    │  ├─ Import Passengers       │
    │  ├─ Import Tickets          │
    │  ├─ Import Orders           │
    │  ├─ Import Loyalty          │
    │  └─ Import Banking          │
    └─────────────────────────────┘
          ▼
    ┌─────────────────────────────┐
    │   Database                  │
    │   ├─ All data imported      │
    │   ├─ Relationships intact   │
    │   └─ Ready for application  │
    └─────────────────────────────┘
          ▼
    Fully Functional Application
```

### Complete Workflow
```
Current Database (db.sqlite3)
    │
    ├─ BACKUP ──────────────────────┐
    │                               │
    ▼                               │
export_db_to_csv.py                 │
    │                               │
    ▼                               │
CSV Files (Backup)                  │
    │                               │
    ├─────────────────────┐         │
    │                     │         │
    ▼                     ▼         ▼
Remove Old DB         (Keep for)  Backup
    │                  Recovery    Location
    │                     │         │
    ▼                     │         ▼
Fresh Environment        │      Safe Storage
    │                     │
    ▼                     │
setup_db_py312.py        │
    │                     │
    ▼                     │
Fresh db.sqlite3         │
    │                     │
    ▼                     │
import_all_from_csv.py   │
    │◄────────────────────┘
    │ (Import from backup)
    ▼
Complete Database Ready
```

---

## 🔄 Tool Interaction Diagram

```
                     ┌─────────────────┐
                     │  Developer / CI │
                     └────────┬────────┘
                              │
                    ┌─────────▼─────────┐
                    │ database_manager  │  (Master Tool)
                    │      .py          │
                    └──────────┬────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
      ┌──────────┐        ┌──────────┐      ┌──────────┐
      │ export   │        │ setup    │      │ import   │
      │ command  │        │ command  │      │ command  │
      └────┬─────┘        └────┬─────┘      └────┬─────┘
           │                   │                   │
           ▼                   ▼                   ▼
      ┌──────────┐        ┌──────────┐      ┌──────────┐
      │export_db │        │setup_db  │      │import_all│
      │_to_csv   │        │_py312    │      │_from_csv │
      │  .py     │        │  .py     │      │  .py     │
      └────┬─────┘        └────┬─────┘      └────┬─────┘
           │                   │                   │
           ▼                   ▼                   ▼
      ┌──────────┐        ┌──────────┐      ┌──────────┐
      │Read from │        │Create &  │      │Read from │
      │Current   │        │Configure │      │CSV Files │
      │Database  │        │Fresh DB  │      └────┬─────┘
      └────┬─────┘        └────┬─────┘            │
           │                   │                   │
           ▼                   ▼                   ▼
      ┌──────────┐        ┌──────────┐      ┌──────────┐
      │Generate  │        │Run       │      │Write to  │
      │CSV Files │        │Migrations│      │Database  │
      └────┬─────┘        └────┬─────┘      └────┬─────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
                               ▼
                         ┌──────────────┐
                         │   Result:    │
                         │ • Backup CSV │
                         │ • Fresh DB   │
                         │ • All Data   │
                         └──────────────┘
```

---

## 📍 Model Relationships

```
┌──────────────────┐
│    User          │────────┐
│ (auth.User)      │        │
└──────────────────┘        │
         │                  │
         ├─────────┐        │
         │         │        │
         ▼         ▼        ▼
    ┌────────┐  ┌──────────────┐  ┌──────────┐
    │ Ticket │  │LoyaltyAccount│  │Order     │
    └────────┘  └──────────────┘  └──────────┘
         │             │                │
         ├─────┬───────┴────┬──────────┘
         │     │            │
         ▼     ▼            ▼
    ┌────────┐ ┌─────────┐ ┌──────────┐
    │Flight  │ │Loyalty  │ │OrderItem │
    │        │ │Tier     │ │          │
    └────┬───┘ └─────────┘ └──────────┘
         │
         ├─────┬──────────┐
         │     │          │
         ▼     ▼          ▼
    ┌─────────┐  ┌──────┐  ┌──────┐
    │Passenger│  │Place │  │Week  │
    │         │  │      │  │      │
    └─────────┘  └──────┘  └──────┘
```

---

## 📂 CSV Schema Diagram

```
┌──────────────────────┐
│ airports.csv         │
├──────────────────────┤
│ • city               │
│ • airport            │
│ • code               │
│ • country            │
└──────────────────────┘

┌──────────────────────┐
│ domestic_flights.csv │
├──────────────────────┤
│ • origin (FK)        │
│ • destination (FK)   │
│ • depart_time        │
│ • arrival_time       │
│ • depart_weekday     │
│ • duration           │
│ • airline            │
│ • flight_number      │
│ • fares              │
└──────────────────────┘

┌──────────────────────┐
│ users.csv            │
├──────────────────────┤
│ • id                 │
│ • username           │
│ • first_name         │
│ • last_name          │
│ • email              │
│ • is_staff           │
│ • is_active          │
└──────────────────────┘

┌──────────────────────┐
│ tickets.csv          │
├──────────────────────┤
│ • id                 │
│ • user_id (FK)       │
│ • flight_id (FK)     │
│ • ref_no             │
│ • seat_class         │
│ • total_fare         │
│ • booking_date       │
│ • status             │
└──────────────────────┘
```

---

## 🔐 Data Integrity Checks

```
Export:
  ✓ Check database connection
  ✓ Verify all tables exist
  ✓ Handle NULL values
  ✓ Escape special characters
  ✓ Maintain data types

Import:
  ✓ Validate CSV format
  ✓ Check foreign keys exist
  ✓ Handle duplicates
  ✓ Preserve relationships
  ✓ Report errors gracefully

Setup:
  ✓ Verify Django project
  ✓ Check Python version
  ✓ Validate migrations
  ✓ Create superuser
  ✓ Initialize config
```

---

## ⏱️ Execution Timeline

```
Full Setup (database_manager.py full-setup)
├─ Backup Creation (5-10 sec)
├─ Export CSV (10-30 sec)
├─ Remove Old DB (1-2 sec)
├─ Django Setup (30-60 sec)
│  ├─ Migrations (20-40 sec)
│  └─ Superuser (5-10 sec)
├─ Import Data (1-5 min)
│  ├─ Places (1-2 sec)
│  ├─ Flights (10-30 sec)
│  ├─ Users (1-2 sec)
│  ├─ Passengers (1-2 sec)
│  ├─ Tickets (5-10 sec)
│  └─ Other (1-5 sec)
└─ Total: 3-10 minutes
```

---

## 🎯 Use Case Scenarios

### Scenario 1: Fresh Development Environment
```
Developer joins → Clones repo → Runs: python database_manager.py setup
Result: Full working database with all data
```

### Scenario 2: Backup Before Major Changes
```
Before changes → Run: python database_manager.py export --output ./backup
After changes → Run: python database_manager.py full-restore --backup-dir ./backup
Result: Safe backup + ability to revert
```

### Scenario 3: Migrate Between Environments
```
Production Export → Copy CSV files → Development Setup
Result: Exact replica in development environment
```

### Scenario 4: CI/CD Pipeline
```
Docker build → Install deps → Run: python database_manager.py setup
Result: Ready-to-test application with data
```

### Scenario 5: Data Disaster Recovery
```
Database corrupted → Have CSV backup → Run: full-restore
Result: Database recovered from backup
```

---

## 🔑 Key Design Principles

1. **Modularity** - Each tool can work independently
2. **Atomicity** - Operations complete fully or rollback
3. **Portability** - CSV format works anywhere
4. **Safety** - Backups created automatically
5. **Simplicity** - One-command workflows
6. **Completeness** - Handles all app data
7. **Flexibility** - Custom paths and options
8. **Robustness** - Graceful error handling

---

## 📊 System State Transitions

```
INITIAL STATE
   ↓
[Developer/CI] → database_manager.py export
   ↓
BACKED_UP_STATE (CSV files created)
   ↓
[Developer/CI] → database_manager.py setup
   ↓
FRESH_DATABASE_STATE (No data yet)
   ↓
[Developer/CI] → database_manager.py import
   ↓
POPULATED_DATABASE_STATE (Ready to use)
   ↓
[Developer] → python manage.py runserver
   ↓
APPLICATION_RUNNING_STATE
```

---

## 🚀 Performance Optimization

```
Export:
  - Sequential table reads
  - Batch CSV writes
  - Memory efficient

Setup:
  - Lazy migration loading
  - Parallel dependency install
  - Minimal config

Import:
  - Bulk operations where possible
  - Foreign key optimization
  - Relationship caching

Overall:
  - Multi-app support (skip unavailable)
  - Error recovery (continue on issues)
  - Progress reporting
```

---

**This architecture ensures robust, reliable, and efficient database management across all environments.**
