# Lifetracker

A Django application for tracking various aspects of your life using best practices.

## Features

- User authentication with email-based login
- Clean, modern UI with Flowbite and Tailwind CSS
- Responsive dashboard with analytics cards
- User profile management with editable name and timezone settings
- SQLite database
- Hero-style landing page for non-authenticated users
- Light/Dark theme toggle with localStorage persistence
- Sticky footer that stays at the bottom of the page

## Technologies Used

- Python 3.12
- Django 5.1+
- Flowbite CSS (CDN)
- SQLite

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd lifetracker
   ```

2. Create a virtual environment and activate it:
   ```
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python3.12 manage.py migrate
   ```

5. Create a superuser (admin):
   ```
   python3.12 manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python3.12 manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Project Structure

- `lifetracker/` - Main project settings
- `users/` - Custom user model and authentication views
- `dashboard/` - Dashboard and analytics functionality
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)

## Usage

1. Register a new account or log in with an existing one
2. Navigate to the dashboard to view your life metrics
3. Update your profile information as needed

## License

MIT 