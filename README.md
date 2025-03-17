# Car Rental System
This is a **Flask-based Car Rental System** that allows users to register, log in, reserve vehicles, make payments, and manage reservations. Admins can add, modify, delete, prices of vechicles and vehicles. Admins can veiw customers reservations.

---

## Installation
### Prerequisites
Ensure **Python 3.6+** is installed and also **pip**.

1. Clone the repository
```sh
git clone https://github.com/JDV1281/Car-Rental-System.git
cd Car-Rental-System
```

2. Create and activate a virtual environmentt (recommended but optional)
```sh
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows
```

3. Install the dependencies
```sh
pip install -r requirements.txt
```

4. Set up the database (database is SQLite)
```sh
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

5. Run the flask app
```sh
python app.py
```

6. Open a browser and go to:
```
http://127.0.0.1:5000/
```

---

## Features

- **User Authentication** - Users can register and log in securely.
- **Vehicle Reservation System** - Users can browse available vehicles, reserve them, and modify/cancel reservations.
- **Admin Dashboard** - Admin users can change vehicle prices. Admins can add, delete, and modify available vehicles.
- **Payment System** - Users can enter payment details to confirm reservations.


---

## Project structure
```
Car-Rental-System/
│── instance/                     # SQLite database instance
│── static/                       # Static assets (CSS, images)
│── templates/                    # HTML Templates
│   ├── admin.html                # Admin dashboard
│   ├── base.html                 # Main template layout
│   ├── dashboard.html            # User dashboard
│   ├── index.html                # Home page
│   ├── login.html                # User and admin login page
│   ├── modify_reservation.html   # Modify user reservation page
│   ├── my_reservations.html      # User reservation page
│   ├── payment.html              # Payment page
│   ├── register.html             # Register page
│   ├── reserve.html              # Reserve page
│── app.py                        # Main application file
│── requirements.txt              # Dependencies list
│── README.md                     # Documentation
│── run_server.bat                # Batch file to run the app on Windows
│── requirements.txt
```

## API Endpoints

| Route                          | Method | Description |
|--------------------------------|--------|-------------|
| `/`                            | GET    | Home page |
| `/register`                    | GET/POST | User and admin registration |
| `/login`                       | GET/POST | User  and admin login |
| `/dashboard`                   | GET    | View available vehicles |
| `/reserve/<int:vehicle_id>`     | GET/POST | Reserve a vehicle |
| `/my_reservations`             | GET    | View user reservations |
| `/cancel_reservation/<int:reservation_id>` | POST | Cancel a reservation |
| `/modify_reservation/<int:reservation_id>` | GET/POST | Modify reservation details |
| `/payment/<int:reservation_id>` | GET/POST | Payment confirmation |
| `/admin`                       | GET    | Admin dashboard |
| `/add_vehicle`                 | POST   | Admin adds a new vehicle and sets price |
| `/delete_vehicle/<int:vehicle_id>` | POST | Admin removes a vehicle and sets price |
| `/logout`                      | GET    | User logout |

## Technologies Used

- **Flask** - Web framework for Python
- **Flask-SQLAlchemy** - ORM for database handling
- **SQLite** - Database for storing user and vehicle information
- **Werkzeug Security** - Secure password hashing
- **Jinja2** - Templating engine for dynamic content
- **Bootstrap (optional)** - Frontend styling

## Future Enhancements

- Add place for cutomer to enter in their email at payment page.
- Add email notifications for reservations.
- To register as a admin, you will need a passcode and not just checking a box that user is an admin.


## Author
Developed by **JDV1281**
Contact: `jdverrick1@gmail.com`
GitHub: [JDV1281](https://github.com/JDV1281/Car-Rental-System)