# AharSetu – Food Donation Platform

**AharSetu** is a web-based platform that connects food donors, such as hotels and restaurants, with orphanages and other organizations in need. The goal is to minimize food wastage by facilitating the donation of surplus food to those who need it most.

## Features

- **Donor Registration & Login:**
  - Donors can sign up, log in, and manage their food donations.
  - Donors post food availability and specify the amount of food, the city, and additional details.
  
- **Beneficiary Registration & Login:**
  - Beneficiaries (e.g., orphanages or organizations) can register, log in, and search for available food donations.
  
- **Food Posting & Management:**
  - Donors can post surplus food details including type, quantity, city, and any additional notes.
  - Donors can manage their active posts, including editing or removing them.
  
- **City-based Search:**
  - Beneficiaries can search for available food donations by city.
  - Only food posts from the last 24 hours are displayed to ensure freshness.
  
- **Real-time Notifications:**
  - Donors are notified when a beneficiary reserves their food.
  - Beneficiaries are updated every 6 hours on available food posts.
  
- **User Profiles:**
  - Donors and beneficiaries have access to their profiles where they can manage their personal details.

- **Additional Features:**
  - Contact Us, Blogs, Feedback, and About Us pages are included to provide extra support and interaction.

## Folder Structure

```bash
├── templates/
│   ├── index.html         # Homepage with a hero section and call-to-action
│   ├── donor_login.html   # Login page for donors
│   ├── beneficiary_login.html  # Login page for beneficiaries
│   ├── food_posts.html    # List of available food posts (searchable by city)
│   ├── profile.html       # Donor and beneficiary profiles
│   └── feedback.html      # Feedback form for users
│   and other ones...
├── static/
│   ├── css/               # Custom CSS stylesheets
│   └── images/            # Images used throughout the web application
│  
│
├── main.py                # Main Flask application file
└── README.md              # This file

## Prerequisites

- Python 3.x
- Flask
- MySQL or any other compatible database
- PyMySQL (or MySQL-connector)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aharsetu.git
2. Navigate to the project directory
   ```bash
   cd aharsetu
3. Install the required dependencies
   ```bash
   pip install -r requirements.txt
4. Set up your database and configure the connection in main.py.
5. Run the Flask application:
   ```bash
   python main.py
6. Open your browser and go to http://127.0.0.1:5000/ to view the application.

## Technologies Used
- Backend: Python, Flask
- Frontend: HTML, CSS, Bootstrap, JavaScript
- Database: MySQL with PyMySQL for database connections
- Icons & Styling: FontAwesome, Bootstrap
