from flask import Flask, request, redirect, flash, render_template, send_file
import smtplib
from email.message import EmailMessage
import pandas as pd
import os, shutil, zipfile
from io import BytesIO
import re
import urllib.parse

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# 🔐 Replace these with your email credentials
ADMIN_EMAIL = 'example@gmail.com'
ADMIN_APP_PASSWORD = 'password'  # App Password generated from Google

@app.route('/')
def home():
    return render_template(
        'home.html',
        hero_text="Modern Digital <br> Solutions for Growth",
        hero_subtext="Unlock your online potential with innovative strategies and expert execution. We build digital foundations for your future.",
    )

@app.route('/about')
def about():
    return render_template('about.html', page_title="About DigiYash")

@app.route('/services')
def services():
    return render_template('services.html', page_title="Our Services")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject", "No Subject")
        message = request.form.get("message")

        # ✅ Email to Admin
        admin_msg = EmailMessage()
        admin_msg['Subject'] = f"[DigiYash Contact] {subject}"
        admin_msg['From'] = ADMIN_EMAIL
        admin_msg['To'] = ADMIN_EMAIL
        admin_msg.set_content(f"""
You received a new contact form submission from the DigiYash website:

👤 Name: {name}
📧 Email: {email}
📝 Subject: {subject}

💬 Message:
{message}
        """)

        # ✅ Auto-reply to the user
        user_msg = EmailMessage()
        user_msg['Subject'] = "Thank you for contacting DigiYash!"
        user_msg['From'] = "DigiYash <yashcybercafeofficial@gmail.com>"
        user_msg['To'] = email
        user_msg.set_content(f"""
Hello {name},

Thank you for reaching out to DigiYash! 🙏
We’ve received your message and our team will get back to you shortly.

If this was a support request, expect a reply within 24–48 hours.

Regards,
✨ DigiYash Team
📍 https://digiyash.pythonanywhere.com
        """)

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(ADMIN_EMAIL, ADMIN_APP_PASSWORD)
                smtp.send_message(admin_msg)
                smtp.send_message(user_msg)
            flash("✅ Your message was sent successfully!", "success")
        except Exception as e:
            print("Email Error:", e)
            flash("❌ Something went wrong. Please try again later.", "error")

        return redirect("/thank_you")

    return render_template('contact.html', page_title="Contact DigiYash")

@app.route("/thank_you")
def thank_you():
    return render_template('thank_you.html', page_title="Thank You!")
    
@app.route("/myself")
def myself():
    return render_template('myself.html', page_title="myself")
    
if __name__ == "__main__":
    app.run(debug=True)
