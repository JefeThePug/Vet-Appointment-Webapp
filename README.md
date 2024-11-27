# Veterinary Appointment Scheduling Webapp for Dr. Pug Animal Clinic

## Description
This web app is a Flask-based series of web pages with access to a SQLite server as its database. It serves as a mock-up for an actual Veterinary Office or Animal Clinic, enabling electronic management and scheduling of appointments, thus eliminating the need for a secretary to take appointments via phone.

## Features
- **User  Registration and Login**: Each user must register a username and password to access the appointment app. Upon loading the page, users are directed to the login screen. New users can register through the Account drop-down menu.
  
- **User  Settings**: After the first login, users are redirected to a settings page to input their email address and register their pets. Users cannot make appointments without at least one registered pet. The settings page also allows users to change their username or password and manage their registered pets.

- **Informative Pages**: The app includes several informative pages:
- **Doctors Page**: Displays a list of doctors at the clinic with photographs and short bios.
- **Access Page**: Provides directions to the clinic, including a Google Maps embed (demonstrative only) and public transportation information.
- **Hours Page**: Shows the clinic's hours of operation, which are retrieved from the database.

- **Appointment Booking**: The main page of the app is the appointment booking page. Users can select a doctor and their pet from drop-down menus. The availability chart displays the next five days, segmented into thirty-minute intervals, indicating availability:
  - Circle (◯): Lots of availability
  - Triangle (△): Limited availability
  - X (✕): No availability

- **Appointment Management**: Users can view, cancel, or delete upcoming appointments. Past appointments are also displayed for reference.

## Folder Structure
- **app.py**: The main Flask application file.
- **support.py**: Contains helper functions to assist the app.
- **reservations.db**: SQLite database containing tables for users, doctors, pets, hours, and bookings.

### Subfolders
- **static/**: Contains images (jpg, png) and icons (ico) used on the website, as well as the `main.js` script for JavaScript functionality and `styles.css` for styling.
- **templates/**: Contains HTML files, with `layout.html` as the main framework using Jinja markup.

## Technologies Used
- **Flask**: Web framework for Python.
- **SQLite**: Lightweight database for storing application data.
- **HTML/CSS**: For structuring and styling the web pages.
- **JavaScript**: For enhancing interactivity within the web app.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/JefeThePug/Vet-Appointment-Webapp.git
   cd Vet-Appointment-Webapp
   ```
2. Install the required packages using `REQUIREMENTS.txt`:
   ```bash
   pip install -r REQUIREMENTS.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## Acknowledgments
This project is my first experience creating a Flask application with a database. It also marks my initial foray into HTML and CSS. I recognize there is room for improvement and welcome any feedback.

Thank you for exploring the Veterinary Appointment Scheduling Webapp!
