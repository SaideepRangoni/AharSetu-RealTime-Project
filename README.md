# AharSetu – Food Donation Platform

**AharSetu** is a web-based platform designed to bridge the gap between food donors, such as restaurants and hotels, and beneficiaries like orphanages and organizations in need. Its primary mission is to reduce food wastage by channeling surplus food to the needy in an efficient and user-friendly manner.

## Features

- **Donor Registration & Login:**
  - Donors can sign up, log in, and manage their food donations.
  - Donors can post food availability with details such as type, quantity, city, and additional notes.

- **Beneficiary Registration & Login:**
  - Beneficiaries (e.g., orphanages or organizations) can register, log in, and search for available food donations.

- **Food Posting & Management:**
  - Donors can post surplus food details, including type, quantity, city, and any additional notes.
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
├── main.py                # Main Flask application file
└── README.md              # This file

```

## Prerequisites

- **Python 3.x**
- **Flask**
- **MySQL** or any other compatible database
- **PyMySQL** (or **MySQL-connector**)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aharsetu.git
   ```
2. Navigate to the project directory:
   ```bash
   cd aharsetu
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your database and configure the connection in main.py.
5. Run the Flask application:
   ```bash
   python main.py
   ```
6. Open your browser and go to http://127.0.0.1:5000/ to view the application.

## Technologies Used
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, Bootstrap, JavaScript
- **Database:** MySQL with PyMySQL for database connections
- **Icons & Styling:** FontAwesome, Bootstrap

## Testing
The platform underwent comprehensive user testing and peer review. The following tests were conducted:

- **User Testing:** Ensured the ease of navigation for both donors and beneficiaries. Verified the accuracy of city-based searches and reservation flows.
- **Peer Review:** Reviewed by peers to check for any usability issues and functionality bugs.

## Video Demonstration
I have created a video showcasing the full functionality of the **AharSetu** platform, including the donor registration process, food post creation, beneficiary search and reservation, and notifications.

## Articles
I have also written an article on Medium, highlighting the goals, development journey, and technical challenges of **AharSetu**. You can find it [here](#).

## Contact Us
For any inquiries or support, feel free to reach out:

- **Email:** saideeprangoni634@gmail.com
- **LinkedIn:** [Your LinkedIn Profile](https://www.linkedin.com/in/saideep-rangoni-54abb9300/)
