PoPutiBot 🚊

 Project Description

 PoPutiBot is a telegram bot for organizing the delivery and transportation of things between cities. Users can choose whether they want to transfer or take an item, specify the size of items and route details, and manage their requests through a user-friendly interface.

 Main functions

 Transfer and transportation of things: Choosing an action ("Transfer" or "Take away") indicating the dimensions and details.

 Route indication: Entering the cities of departure and destination.

 Data storage: All queries are stored in the SQLite database.

 Notifications: Users receive notifications about suitable carriers.

 Database Cleanup: Automatic weekly cleanup of old records using the scheduler.

PoPutiBot/
```├── bot/```
│   ├── __init__.py
│   ├── database.py       # Database management
│   ├── handlers.py       # Core logic for user interactions
│   ├── scheduler.py      # Scheduler for automatic database cleanup
│   └── requests.db       # SQLite database file
├── Main.py               # Main bot launch file
└── requirements.txt      # Project dependencies



Key Features

Complexity and Creativity:

Object-oriented approach to separate sending and transportation logic.

Integration with a task scheduler for automatic database cleanup.

Technical Implementation:

Use of telegram.ext, sqlite3, aioschedule, and asyncio modules.

Asynchronous function implementation for smooth bot operation.

Functionality:

Support for various item size scenarios.

Data storage in the database with options for viewing and deletion.

Code Quality:

Clean, well-structured code with comments.

Modular design for easy maintenance and expansion.

Timeliness:

Adherence to all deadlines with regular project updates.
