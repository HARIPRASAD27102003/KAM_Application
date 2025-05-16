## Project Overview

This project is a **Restaurant Performance Management System** designed to track, evaluate, and improve the performance of restaurants. It offers a comprehensive view of each restaurant's performance based on various metrics such as order success rate, interaction frequency, and call compliance. The system allows restaurant managers and key account managers (KAMs) to monitor performance, identify areas for improvement, and classify restaurants into performance categories such as **Excellent**, **Good**, **Average**, **Underperforming**, and **Critical**.

### Key Features:
- **Restaurant Management**: Create and manage restaurant records, including basic details such as name, address, region, and operational status.
- **Order Tracking**: Keep track of all orders with their status, helping to evaluate performance based on order completion rate.
- **Interaction Tracking**: Monitor the interactions (calls, meetings, emails) between the restaurant and KAMs.
- **Call Frequency Management**: Schedule and manage the frequency of calls to ensure proper follow-up with each restaurant.
- **Performance Metrics**: Automatically calculate and categorize restaurant performance based on predefined thresholds for order success rate, interaction frequency, and call compliance.
- **Visual Representation**: Display restaurant performance using colorful, categorized cards based on performance status.

This system helps businesses streamline restaurant performance management, ensuring timely follow-ups and efficient communication with the goal of improving customer satisfaction and operational efficiency.

Here’s an example of a **System Requirements** section for your README:

---

## System Requirements

To run the Restaurant Performance Management System, ensure that your environment meets the following requirements:

### Software Requirements:
- **Python**: 3.8 or higher
- **Django**: 3.x or higher
- **Django Rest Framework**: 3.x or higher (if you are exposing APIs)
- **pytz**: For handling timezone-related operations
- **PostgreSQL** (or another database of your choice):
  - **SQLite** is used by default for development, but for production, PostgreSQL or MySQL is recommended.
  
### Frontend Requirements (if applicable):
- **HTML/CSS/JavaScript**: For frontend rendering and UI components
- **Bootstrap 4/5**: For responsive and styled UI components
  

### Installation Dependencies:
To install all necessary dependencies, use the following command:
```bash
pip install -r requirements.txt
```

### Database Setup:
Ensure that you have a running PostgreSQL or MySQL instance for production. For development purposes, SQLite is configured by default.

Here’s an example of **Installation Instructions** for your README:

---

## Installation Instructions

Follow the steps below to set up the Restaurant Performance Management System on your local machine or server.

### Step 1: Clone the Repository
First, clone the project repository to your local machine:
```bash
cd app
```

### Step 2: Set Up a Virtual Environment (Optional but Recommended)
It's highly recommended to use a virtual environment to manage dependencies and avoid conflicts with other projects.

1. Create a virtual environment:
   - For Windows:
     ```bash
     python -m venv venv
     ```
   - For macOS/Linux:
     ```bash
     python3 -m venv venv
     ```

2. Activate the virtual environment:
   - For Windows:
     ```bash
     venv\Scripts\activate
     ```
   - For macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

### Step 3: Install Dependencies
Install all the required Python packages using `pip`:
```bash
pip install -r requirements.txt
```

### Step 4: Set Up the Database
Run the following commands to set up the database and apply any migrations:

1. Make migrations:
   ```bash
   python manage.py makemigrations
   ```

2. Apply migrations:
   ```bash
   python manage.py migrate
   ```
3. Create a Cache table:(To use like cache)
   ```bash
   python manage.py createcachetable
   ```

### Step 5: Create a Superuser (Optional)
To access the Django admin panel, create a superuser by running:
```bash
python manage.py createsuperuser
```
Follow the prompts to set up a username, email, and password for the admin user.


### Step 6: Running Celery and Celery Beat(for time being I have set the interval of the tasks by 10 seconds)

  Follow the steps below to start Celery and Celery Beat in your Django project:

  1. Start the Celery Worker
  Run the following command to start the Celery worker:

  ```bash
  celery -A app worker --loglevel=info
  ```

  2. Start the Celery Beat Scheduler
  Run the following command to start the Celery Beat scheduler::

  ```bash
  celery -A app beat --loglevel=info

### Step 7: Run the Development Server
  Start the Django development server:

  ```bash
  python manage.py runserver
  ```
  This will start the server on `http://127.0.0.1:8000/`. You can now access the project in your browser.


### Step 8: Access the Admin Panel
Visit the Django admin panel at `http://127.0.0.1:8000/admin/` and log in with the superuser credentials you created earlier.


## API Documentation

Below is the list of API endpoints for the Restaurant Performance Management System. These endpoints allow interaction with the system, including user authentication, restaurant management, and performance tracking.

### **Authentication & User Management**
- **`POST /signup/`**  
  Registers a new user.  
  **Payload:** `username`, `email`, `password`

- **`POST /login/`**  
  Logs in an existing user and returns an authentication token.  
  **Payload:** `username`, `password`

- **`GET /logout/`**  
  Logs out the current user and invalidates the authentication token.

- **`GET /profile/`**  
  Retrieves the profile details of the logged-in user.

### **Restaurant Management**
- **`GET /restaurant/<str:restaurant_name>/`**  
  Retrieves detailed information about a specific restaurant.  
  **URL Parameter:** `restaurant_name` - Name of the restaurant

- **`POST /add_restaurant/`**  
  Adds a new restaurant to the system.  
  **Payload:** `name`, `address`, `contact details`, and other necessary restaurant information.

- **`GET /restaurant/<str:restaurant_name>/pending-orders/`**  
  Retrieves a list of pending orders for a specific restaurant.  
  **URL Parameter:** `restaurant_name` - Name of the restaurant

- **`POST /restaurant/<str:restaurant_name>/change-lead/`**  
  Changes the lead of the restaurant.  
  **URL Parameter:** `restaurant_name` - Name of the restaurant  
  **Payload:** `new_lead` - New lead’s name or identifier

- **`POST /restaurant/<str:restaurant_name>/add_contact/`**  
  Adds a new contact to the restaurant.  
  **URL Parameter:** `restaurant_name` - Name of the restaurant  
  **Payload:** `contact_details` - Information about the new contact

- **`GET /restaurant/<str:restaurant_name>/orders/`**  
  Retrieves a list of orders for the restaurant.  
  **URL Parameter:** `restaurant_name` - Name of the restaurant

- **`GET /restaurant/<str:restaurant_name>/interactions`**  
  Retrieves a list of interactions with the restaurant.  
  **URL Parameter:** `restaurant_name` - Name of the restaurant

- **`POST /restaurant/<str:restaurant_name>/add_interaction/`**  
  Adds an interaction for the restaurant.  
  **URL Parameter:** `restaurant_name` - Name of the restaurant  
  **Payload:** `interaction_details` - Details about the interaction

### **Calls and Scheduling**
- **`GET /future-calls/`**  
  Retrieves a list of upcoming calls that are scheduled.

- **`GET /todo-calls/`**  
  Retrieves a list of calls that need to be made.

- **`GET /pending-calls/`**  
  Retrieves a list of pending calls.

### **Interactions**
- **`GET /interactions/`**  
  Retrieves a list of all interactions in the system.

- **`GET /all-interactions/`**  
  Retrieves a comprehensive list of all interactions across restaurants.

### **Performance**
- **`GET /performance/`**  
  Retrieves the performance data for all restaurants, including performance score and status.


###To view the list of all available routes and their corresponding URLs in the application, visit the following route:

**URL:** `/api-documentation/`

    This page provides a structured overview of all the API paths, which can be useful for developers to understand and interact with the available endpoints in the application.

    Simply navigate to `/api-documentation/` in your browser to access the full list.

---

Each of the above endpoints allows various actions like retrieving information, adding new records, or modifying existing data. The responses will typically be in JSON format, providing either the requested data or confirmation of successful action.

For more detailed information on how to interact with each of these API endpoints, refer to the specific documentation provided in your project.





