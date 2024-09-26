from flask import Flask, jsonify, render_template, request, redirect, url_for, g, session, flash
import io
import base64
import matplotlib.pyplot as plt
import mysql.connector
import os,pymysql
import logging
import json
import secrets
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import datetime, timedelta
import threading
import time





app = Flask(__name__)
app.secret_key = "helloworld"  # Secret key for session management

# MySQL Database connection
db = pymysql.connect(
    host="localhost",
    user="root",
    password="9666099560",
    database="mydatabase"
)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Mail server
app.config['MAIL_PORT'] = 587  # Mail port
app.config['MAIL_USERNAME'] = 'saideeprangoni634@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'ivuv epqn vsov baay'  # Your app password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False  # Ensure this is False
app.config['DEBUG'] = True

mail = Mail(app)


# Home route
@app.route('/')
def home():
    return render_template('index.html')


########################################
###### Beneficiary related routings 


@app.route('/beneficiary_registration', methods=['GET', 'POST'])
def beneficiary_registration():
    if request.method == 'POST':
        username = request.form.get('username')
        contact = request.form.get('contact')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        city = request.form.get('cityField')

        # Validate password
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('beneficiary_registration'))

        # Insert beneficiary into the database without hashing (consider hashing in production)
        try:
            cursor = db.cursor()
            insert_query = """
                INSERT INTO beneficiary (username, contact, email, password, city)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (username, contact, email, password, city))  # Storing raw password
            db.commit()
            cursor.close()

            flash('Registration successful!', 'success')
            return redirect(url_for('beneficiary_login'))

        except Exception as err:
            db.rollback()
            flash(f'Database error: {str(err)}', 'danger')
            return redirect(url_for('beneficiary_registration'))

    return render_template('beneficiary_registration.html')
@app.route('/beneficiary_login', methods=['GET', 'POST'])
def beneficiary_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')  # Plain text password comparison

        try:
            # Cursor setup to execute MySQL commands
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                # Query to fetch beneficiary by email
                sql = "SELECT * FROM beneficiary WHERE email = %s"
                cursor.execute(sql, (email,))
                beneficiary = cursor.fetchone()

                # Check if the beneficiary exists and compare the plain text password
                if beneficiary and beneficiary['password'] == password:
                    session['beneficiary_id'] = beneficiary['id']  # Storing session for beneficiary
                    session['email'] = beneficiary['email']
                    flash('Login successful!', 'success')
                    return redirect(url_for('landingpage_beneficiary'))  # Redirect to beneficiary landing page
                else:
                    flash('Invalid email or password.', 'danger')
                    return redirect(url_for('beneficiary_login'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            return redirect(url_for('beneficiary_login'))
    
    return render_template('beneficiary_login.html')
@app.route('/landingpage_beneficiary', methods=['GET', 'POST'])
def landingpage_beneficiary():
    # Check if the beneficiary is logged in using beneficiary_id
    if 'beneficiary_id' not in session:
        return redirect(url_for('beneficiary_login'))

    return render_template('landingpage_beneficiary.html')




@app.route('/search_for_food', methods=['GET', 'POST'])
def search_for_food():
    if 'beneficiary_id' not in session:
        return redirect(url_for('beneficiary_login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        city = request.form.get('city')
        beneficiary_id = session['beneficiary_id']

        try:
            conn = db  # Assuming db is your database connection
            with conn.cursor() as cursor:
                twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

                query = """
                SELECT id, food_details, city, people_served
                FROM food_posts
                WHERE city = %s AND created_at > %s
                """
                cursor.execute(query, (city, twenty_four_hours_ago))
                food_posts = cursor.fetchall()

                results = [
                    {
                        "id": post[0],
                        "food_details": post[1],
                        "city": post[2],
                        "people_served": post[3]
                    }
                    for post in food_posts
                ]

                return jsonify({"food_posts": results})

        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return jsonify({"error": "An error occurred while fetching data."}), 500

    return render_template('searchforfood.html')  # Render the search page directly for GET requests


@app.route('/view_details/<int:post_id>', methods=['GET'])
def view_details(post_id):
    try:
        with db.cursor() as cursor:
            query = """SELECT u.username, u.contact, u.email 
                FROM food_posts fp 
                JOIN users u ON fp.username = u.email 
                WHERE fp.id = %s"""
            cursor.execute(query, (post_id,))
            result = cursor.fetchone()
            if result:
                return jsonify({"username": result[0], "contact": result[1], "email": result[2]})
            else:
                return jsonify({"error": "Post not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reserve/<int:post_id>', methods=['GET'])
def reserve_food(post_id):
    try:
        with db.cursor() as cursor:
            query = """SELECT u.email 
                       FROM food_posts fp 
                       JOIN users u ON fp.username = u.email 
                       WHERE fp.id = %s"""
            cursor.execute(query, (post_id,))
            result = cursor.fetchone()

            if result:
                donor_email = result[0]
                print(f"Donor email found: {donor_email}")  # Log found email

                # Send confirmation email to the donor
                send_email_to_donor(donor_email)

                return jsonify({"success": True})
            else:
                print("Post not found.")  # Log if post is not found
                return jsonify({"error": "Post not found."}), 404
    except Exception as e:
        print(f"Error reserving food: {e}")
        return jsonify({"error": str(e)}), 500

def send_email_to_donor(donor_email):
    subject = "Food Reservation Confirmation"
    body = "Someone has reserved the food you posted.They will contact you soon.thank you for your kindness...."
    
    msg = Message(subject, sender='saideeprangoni634@gmail.com', recipients=[donor_email])
    msg.body = body
    try:
        mail.send(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")  # Log the error

@app.route('/beneficiary_profile', methods=['GET', 'POST'])
def beneficiary_profile():
    beneficiary_id = session.get('beneficiary_id')
    if not beneficiary_id:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('beneficiary_login'))

    # Fetch beneficiary data from the database
    cursor = db.cursor()
    cursor.execute("SELECT username, contact, email, city FROM beneficiary WHERE id = %s", (beneficiary_id,))
    beneficiary = cursor.fetchone()

    # Assigning the fetched data to a dictionary for rendering
    beneficiary = {
        'username': beneficiary[0],
        'contact': beneficiary[1],
        'email': beneficiary[2],
        'city': beneficiary[3]
    }

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        # Check current password
        cursor.execute("SELECT password FROM beneficiary WHERE id = %s", (beneficiary_id,))
        stored_password = cursor.fetchone()[0]
        
        if stored_password == current_password:  # Adjust this line for hashed passwords
            cursor.execute("UPDATE beneficiary SET password = %s WHERE id = %s", (new_password, beneficiary_id))
            db.commit()
            flash('Password updated successfully!', 'success')
        else:
            flash('Current password is incorrect.', 'danger')

    return render_template('beneficiary_profile.html', beneficiary=beneficiary)
@app.route('/update_beneficiary_password', methods=['POST'])
def update_beneficiary_password():
    beneficiary_id = session.get('beneficiary_id')
    if not beneficiary_id:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('beneficiary_login'))

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    # Logic to check the current password
    cursor = db.cursor()
    cursor.execute("SELECT password FROM beneficiary WHERE id = %s", (beneficiary_id,))
    result = cursor.fetchone()
    
    if result:
        stored_password = result[0]
        if stored_password == current_password:  # Adjust this line for hashed passwords
            cursor.execute("UPDATE beneficiary SET password = %s WHERE id = %s", (new_password, beneficiary_id))
            db.commit()
            flash('Password updated successfully!', 'success')
        else:
            flash('Current password is incorrect.', 'danger')
    else:
        flash('Beneficiary not found.', 'danger')

    return redirect(url_for('beneficiary_profile'))




#####################################################

#####################################################
### User related routings ####
@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'POST':
        username = request.form['username']
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        city = request.form['cityField']

        # Simple password match validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('user_registration'))

        # Inserting raw password into the database without hashing
        try:
            with db.cursor() as cursor:
                sql = """
                INSERT INTO users (username, contact, email, password, city)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (username, contact, email, password, city))  # Storing raw password
                db.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('user_login'))
        except Exception as e:
            print(e)
            flash('There was an issue creating your account. Please try again.', 'danger')
            return redirect(url_for('user_registration'))

    return render_template('user_registration.html')

       
        


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')  # Plain text password comparison
        
        try:
            # Cursor setup to execute MySQL commands
            with db.cursor(pymysql.cursors.DictCursor) as cursor:
                # Query to fetch user by email
                sql = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()

                # Check if the user exists and compare the plain text password
                if user and user['password'] == password:
                    session['user_id'] = user['id']
                    session['email'] = user['email']
                    flash('Login successful!', 'success')
                    return redirect(url_for('landingpage_user'))  # Replace with your dashboard route
                else:
                    flash('Invalid email or password.', 'danger')
                    return redirect(url_for('user_login'))  # Back to login if credentials fail

        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            return redirect(url_for('user_login'))
    
    # If it's a GET request, render the login form
    return render_template('user_login.html')

@app.route('/landingpage_user')
def landingpage_user():
    if 'user_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('user_login'))
    return render_template('landingpage_user.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('user_login'))

    cursor = db.cursor()
    cursor.execute("SELECT username, contact, email, city FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    user = {
        'username': user[0],
        'contact': user[1],
        'email': user[2],
        'city': user[3]
    }

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        # Check current password and update if valid (add your password checking logic)
        # Example:
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        stored_password = cursor.fetchone()[0]
        if stored_password == current_password:  # Adjust this line for hashed passwords
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
            db.commit()
            flash('Password updated successfully!', 'success')
        else:
            flash('Current password is incorrect.', 'danger')

    return render_template('user_profile.html', user=user)

@app.route('/update_password', methods=['POST'])
def update_password():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('user_login'))

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    # Here, implement your logic to check the current password
    cursor = db.cursor()
    cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    
    if result:
        stored_password = result[0]
        if stored_password == current_password:  # Adjust this line for hashed passwords
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
            db.commit()
            flash('Password updated successfully!', 'success')
        else:
            flash('Current password is incorrect.', 'danger')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('profile'))

@app.route('/donations', methods=['GET'])
def donations():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('user_login'))

    user_id = session['user_id']

    try:
        conn = db  # Ensure db is a valid connection object
        with conn.cursor() as cursor:  # Using 'with' to ensure the cursor is closed automatically

            # Get timestamp for 24 hours ago
            twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

            # Query to fetch food posts by the user in the last 24 hours
            query = """
            SELECT id, food_details, city, people_served, additional_notes, created_at
            FROM food_posts 
            WHERE username = (SELECT email FROM users WHERE id = %s)
            AND created_at > %s
            ORDER BY created_at DESC
            """
            cursor.execute(query, (user_id, twenty_four_hours_ago))

            # Fetching the results
            columns = [column[0] for column in cursor.description]
            food_posts = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # If no posts are found, show a message
            if not food_posts:
                flash('No food posts available in the last 24 hours.', 'info')

    except pymysql.MySQLError as e:
        # Log the error and return JSON if required
        print(f"Database error: {e}")
        return jsonify({'status': 'error', 'message': 'Database error occurred'}), 500

    # Render the template with the food posts or an empty list
    return render_template('donations.html', food_posts=food_posts)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('user_login'))

    user_id = session['user_id']

    try:
        conn = db  # Ensure db is a valid connection object
        with conn.cursor() as cursor:  # Using 'with' to ensure the cursor is closed automatically

            # Delete the post only if it belongs to the logged-in user
            cursor.execute("""
                DELETE FROM food_posts 
                WHERE id = %s AND username = (SELECT email FROM users WHERE id = %s)
            """, (post_id, user_id))

            deleted_rows = cursor.rowcount
            conn.commit()

            if deleted_rows > 0:
                flash('Post deleted successfully!', 'success')
            else:
                flash('Post not found or you do not have permission to delete it.', 'danger')

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        flash('An error occurred while deleting the post. Please try again.', 'danger')
        return jsonify({'status': 'error', 'message': 'Database error occurred'}), 500

    # Redirect to the dashboard page after deletion
    return redirect(url_for('landingpage_user'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/post_availability', methods=['POST'])
def post_availability():
    if request.method == 'POST':
        food_details = request.form.get('food_details')
        people_served = request.form.get('people_served')
        city = request.form.get('city')
        additional_notes = request.form.get('additional_notes')

        # Get username from the session (ensure the user is logged in)
        username = session.get('email')

        if not username:  # Check if the user is logged in
            flash('You need to log in first.', 'danger')
            return redirect(url_for('user_login'))

        try:
            cursor = db.cursor()
            query = """
                INSERT INTO food_posts (username, food_details, people_served, city, additional_notes)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (username, food_details, people_served, city, additional_notes))
            db.commit()
            flash('Food availability posted successfully!', 'success')

            # Redirect to the thank you page after successful insert
            return redirect(url_for('thank_you'))
        except Exception as e:
            db.rollback()
            print(f"Database Error: {str(e)}")  # Log the detailed error
            flash('Error posting food availability: {}'.format(str(e)), 'danger')

        return redirect(url_for('landingpage_user'))
    

#####################################################



# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    cursor = None  # Initialize cursor to None to avoid UnboundLocalError

    if request.method == 'POST':
        email = request.form.get('email')

        try:
            # Establish a database connection
            conn = db  # Ensure this points to your database connection
            cursor = conn.cursor()

            # Check if the email exists in the users table
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                # Generate a random token for password reset
                token = secrets.token_urlsafe(20)

                # Store the reset token in the password_resets table
                cursor.execute(
                    "INSERT INTO password_resets (email, token, expires_at) VALUES (%s, %s, NOW() + INTERVAL 1 HOUR)",
                    (email, token)
                )
                conn.commit()

                # Construct the reset URL
                reset_url = url_for('reset_password', token=token, _external=True)

                # Create the email message
                msg = Message(
                    subject="Password Reset Request",
                    recipients=[email],
                    sender=app.config['MAIL_USERNAME']  # Ensure this is configured correctly
                )
                msg.body = f"To reset your password, visit the following link: {reset_url}"

                # Try to send the email
                try:
                    mail.send(msg)
                    flash('A password reset link has been sent to your email.', 'success')
                    return redirect(url_for('user_login'))
                except Exception as e:
                    app.logger.error(f"Error sending email: {e}")
                    conn.rollback()  # Rollback in case of email sending failure
                    flash('An error occurred while sending the email. Please try again.', 'danger')
            else:
                flash('Email not found.', 'danger')

        except pymysql.MySQLError as err:
            app.logger.error(f"Database Error: {err}")
            flash('An error occurred during the request. Please try again later.', 'danger')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = None
    cursor = None

    if request.method == 'POST':
        new_password = request.form.get('password')

        # Validate the new password
        if not new_password:
            flash('Password cannot be empty.', 'danger')
            return render_template('reset_password.html', token=token)

        try:
            # Establish a database connection
            conn = db  # Ensure this points to your database connection
            cursor = conn.cursor()

            # Verify the reset token exists and is valid (within expiration time)
            cursor.execute("SELECT email FROM password_resets WHERE token = %s AND expires_at > NOW()", (token,))
            result = cursor.fetchone()

            if result:
                email = result[0]  # Get the email from the tuple

                # Update the user's password based on the email (without hashing)
                cursor.execute(
                    "UPDATE users SET password = %s WHERE email = %s",
                    (new_password, email)  # Store the new password directly
                )
                conn.commit()

                # Delete the token after the password reset is successful
                cursor.execute("DELETE FROM password_resets WHERE token = %s", (token,))
                conn.commit()

                flash('Your password has been reset. Please log in.', 'success')
                return redirect(url_for('user_login'))
            else:
                flash('Invalid or expired token.', 'danger')

        except pymysql.MySQLError as err:
            app.logger.error(f"Database Error: {err}")
            flash('An error occurred during the password reset process.', 'danger')

        finally:
            # Close the cursor and connection safely
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('reset_password.html', token=token)


@app.route('/update_password_', methods=['GET', 'POST'])
def update_password_():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        
        # Connect to the database
        connection = db
        try:
            with connection.cursor() as cursor:
                # Update the user's password in the 'users' table
                update_query = "UPDATE users SET password=%s WHERE email=%s"
                cursor.execute(update_query, (new_password, email))
                connection.commit()
                
                if cursor.rowcount == 0:
                    flash('No user found with this email address.', 'warning')
                else:
                    flash('Password updated successfully!', 'success')

        except Exception as e:
            flash('An error occurred while updating the password. Please try again.', 'danger')
        finally:
            connection.close()
        
        return redirect(url_for('user_login'))  # Redirect to login or another page as needed

    return render_template('update_password.html')  # Render the update password form

#######################################################################################################################################################################################################################################
#########beneficiary##################
@app.route('/forgot-password-beneficiary', methods=['GET', 'POST'])
def forgot_password_beneficiary():
    if request.method == 'POST':
        email = request.form.get('email')

        conn = None
        cursor = None

        try:
            # Establish a database connection
            conn = db  # Ensure this points to your database connection
            cursor = conn.cursor()

            # Check if the email exists in the beneficiary table
            cursor.execute("SELECT * FROM beneficiary WHERE email = %s", (email,))
            beneficiary = cursor.fetchone()

            if beneficiary:
                # Generate a random token for password reset
                token = secrets.token_urlsafe(20)

                # Store the reset token in the password_resets table
                cursor.execute(
                    "INSERT INTO password_resetsb (email, token, expires_at) VALUES (%s, %s, NOW() + INTERVAL 1 HOUR)",
                    (email, token)
                )
                conn.commit()

                # Construct the reset URL
                reset_url = url_for('reset_password_beneficiary', token=token, _external=True)

                # Create the email message
                msg = Message(
                    subject="Password Reset Request for Beneficiary",
                    recipients=[email],
                    sender=app.config['MAIL_USERNAME']  # Ensure this is configured correctly
                )
                msg.body = f"To reset your password, visit the following link: {reset_url}"

                # Try to send the email
                try:
                    mail.send(msg)
                    flash('A password reset link has been sent to your email.', 'success')
                    return redirect(url_for('beneficiary_login'))
                except Exception as e:
                    app.logger.error(f"Error sending email: {e}")
                    conn.rollback()  # Rollback in case of email sending failure
                    flash('An error occurred while sending the email. Please try again.', 'danger')
            else:
                flash('Email not found.', 'danger')

        except pymysql.MySQLError as err:
            app.logger.error(f"Database Error: {err}")
            flash('An error occurred during the request. Please try again later.', 'danger')
        finally:
            # Ensure the cursor and connection are closed properly
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    return render_template('forgot_password_beneficiary.html')

@app.route('/reset-password-beneficiary/<token>', methods=['GET', 'POST'])
def reset_password_beneficiary(token):
    conn = None
    cursor = None

    if request.method == 'POST':
        new_password = request.form.get('password')

        # Validate the new password
        if not new_password:
            flash('Password cannot be empty.', 'danger')
            return render_template('reset_password_beneficiary.html', token=token)

        try:
            # Establish a database connection
            conn = db  # Ensure this points to your database connection
            cursor = conn.cursor()

            # Verify the reset token exists and is valid (within expiration time)
            cursor.execute("SELECT email FROM password_resetsb WHERE token = %s AND expires_at > NOW()", (token,))
            result = cursor.fetchone()

            if result:
                email = result[0]  # Get the email from the tuple

                # Update the beneficiary's password based on the email (without hashing)
                cursor.execute(
                    "UPDATE beneficiary SET password = %s WHERE email = %s",
                    (new_password, email)  # Store the new password directly
                )
                conn.commit()

                # Check if the password update was successful
                if cursor.rowcount == 0:
                    flash('No beneficiary found with that email.', 'danger')
                    return render_template('reset_password_beneficiary.html', token=token)

                # Delete the token after the password reset is successful
                cursor.execute("DELETE FROM password_resetsb WHERE token = %s", (token,))
                conn.commit()

                flash('Your password has been reset. Please log in.', 'success')
                return redirect(url_for('beneficiary_login'))
            else:
                flash('Invalid or expired token.', 'danger')

        except pymysql.MySQLError as err:
            app.logger.error(f"Database Error: {err}")
            flash('An error occurred during the password reset process.', 'danger')

        finally:
            # Close the cursor and connection safely
            if cursor:
                cursor.close()
            if conn and conn.open:  # Check if the connection is still open before closing
                conn.close()

    return render_template('reset_password_beneficiary.html', token=token)

@app.route('/update_password_beneficiary', methods=['GET', 'POST'])
def update_password_beneficiary():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')

        # Connect to the database
        connection = db
        try:
            with connection.cursor() as cursor:
                # Update the beneficiary's password in the 'beneficiaries' table
                update_query = "UPDATE beneficiary SET password=%s WHERE email=%s"
                cursor.execute(update_query, (new_password, email))
                connection.commit()

                if cursor.rowcount == 0:
                    flash('No beneficiary found with this email address.', 'warning')
                else:
                    flash('Password updated successfully!', 'success')

        except Exception as e:
            flash('An error occurred while updating the password. Please try again.', 'danger')
        finally:
            connection.close()

        return redirect(url_for('beneficiary_login'))  # Redirect to login or another page as needed

    return render_template('update_password_beneficiary.html')  # Render the update password form

# Route for Learn More page
@app.route('/learnmore')
def learn_more():
    return render_template('learnmore.html')

# Route for Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route for About page
@app.route('/about')
def about():
    return render_template('about.html')

# Blog Page route with Pie Chart
@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/feedback_thank_you')
def feedback_thank_you():
    return render_template('feedback_thank_you.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    # Get the form data
    name = request.form.get('name')
    rating = request.form.get('rating')
    category = request.form.get('category')
    feedback = request.form.get('feedback')
    
    # Get current timestamp for 'created_at'
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert feedback into the database
    conn, cursor = db()
    if conn is None:
        return "Database connection error", 500
    
    query = """
        INSERT INTO feedback (name, rating, category, feedback, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (name, rating, category, feedback, created_at)

    try:
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while submitting feedback", 500

    return redirect(url_for('feedback_thank_you'))


if __name__ == '__main__':
    app.run(debug=True)
