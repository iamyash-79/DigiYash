from flask import Flask, request, redirect, flash, render_template, send_file, json
import smtplib
from email.message import EmailMessage
import pandas as pd
import os, shutil, zipfile
from io import BytesIO
import re
import urllib.parse

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

MAIL_HOST = "mail.sahuone.com"   # ✅ Your cPanel mail server
MAIL_PORT = 465                     # SSL Port
MAIL_USER = "hello@sahuone.com"
MAIL_PASSWORD = "Yashwant@7987"

# ---------- ROBOTS & SITEMAP ----------
@app.route("/robots.txt")
def robots_txt():
    content = "User-agent: *\nDisallow: /owner/\nSitemap: https://sahuone.com/sitemap.xml"
    return Response(content, mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap():
    urls = [
        "https://digiyash.tech/",
        "http://digiyash.tech/philosophy",
        "http://digiyash.tech/expertise",
        "http://digiyash.tech/connect",
        "http://digiyash.tech/work"
    ]
    sitemap_xml = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
    ]
    for url in urls:
        sitemap_xml.append(f"  <url><loc>{url}</loc></url>")
    sitemap_xml.append("</urlset>")
    return Response("\n".join(sitemap_xml), mimetype="application/xml")
    
@app.route('/')
def home():
    return render_template(
        'showcase.html',

        # HERO CONTENT
        hero_text="Modern Digital <br> Solutions for Growth",
        hero_subtext="Unlock your online potential with innovative strategies and expert execution. We build digital foundations for your future.",

        # SEO
        seo_title="SahuOne Technologies – Web Development & Digital Solutions",
        seo_description="SahuOne is a professional website developer in India offering modern web development, business websites, web apps, and digital solutions for startups and businesses.",
       seo_keywords="website developer, web developer, website developer india, web developer india, professional website developer india, best website developer in india, freelance website developer india, website development company india, web design and development india, custom website developer india, business website developer india, startup website developer india, full stack developer india, python website developer india, flask developer india, django developer india, modern website developer india, responsive website developer india, seo friendly website developer india, secure website developer india, fast website developer india, affordable website developer india, website developer chhattisgarh, website developer in chhattisgarh, website developer cg, best website developer chhattisgarh, website developer raipur, website developer raipur cg, best website developer raipur, professional website developer raipur, website designer raipur, website developer dhamtari, website developer dhamtari cg, best website developer dhamtari, website designer dhamtari, website developer bilaspur, website developer bilaspur cg, website developer durg, website developer durg cg, website developer bhilai, website developer bhilai cg, website developer korba, website developer jagdalpur, website developer ambikapur, website developer raigarh, website developer in madhya pradesh, website developer mp, best website developer mp, website developer bhopal, website developer indore, website developer jabalpur, website developer gwalior, website developer ujjain, website developer satna, website developer rewa, website developer katni, website developer in uttar pradesh, website developer up, best website developer up, website developer lucknow, website developer kanpur, website developer noida, website developer greater noida, website developer ghaziabad, website developer varanasi, website developer prayagraj, website developer gorakhpur, website developer ayodhya, website developer agra, website developer mathura, website developer bareilly, website developer for small business, website developer for startups, website developer for shop, website developer for company, website developer for agency, website developer for digital business, website developer for service business, website developer for local business, website developer for travel agency, website developer for solar business, website developer for education institute, website developer for school, website developer for college, website developer for hospital, website developer for clinic, website developer for hotel, website developer for resort, website developer for restaurant, website developer for real estate, website developer for builder, website developer for ecommerce, ecommerce website developer india, online store developer india, business website development, portfolio website developer, company website developer, static website developer, dynamic website developer, custom website development, web application developer india, admin panel developer india, dashboard developer india, crm website developer india, cms website developer india, payment gateway integration developer, razorpay integration developer, stripe integration developer, paypal integration developer, contact form development, api integration developer india, custom flask web app developer, python flask web developer india, website maintenance services india, website redesign services india, website speed optimization, seo optimized website developer, mobile friendly website developer, fast loading website developer, secure web application developer, scalable web application developer, modern ui ux website developer, html css website developer, javascript website developer, bootstrap website developer, tailwind website developer, react website developer india, mysql website developer, sqlite website developer, api based website developer, backend developer india, frontend developer india, full stack web developer india, hire website developer india, hire website developer raipur, hire website developer chhattisgarh, hire freelance website developer india, low cost website developer india, cheap website developer india, affordable website developer india, trusted website developer india, reliable website developer india, experienced website developer india, best web developer india, top website developer india, SahuOne, SahuOne, SahuOne, SahuOne website developer, SahuOne web development, SahuOne digital solutions, SahuOne tech, SahuOne india, SahuOne website services, SahuOne web agency, SahuOne digital india, best website developer SahuOne, SahuOne raipur, SahuOne dhamtari, SahuOne chhattisgarh",
        seo_h1="Professional Website Developer & Digital Solutions Provider"
    )

@app.route('/philosophy')
def philosophy():
    return render_template('philosophy.html', page_title="About SahuOne")

@app.route('/expertise')
def expertise():
    return render_template('expertise.html', page_title="Our Services")
    
@app.route("/connect", methods=["GET", "POST"])
def connect():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject", "No Subject")
        message = request.form.get("message")

        # Email to Admin
        admin_msg = EmailMessage()
        admin_msg["Subject"] = f"[SahuOne Contact] {subject}"
        admin_msg["From"] = MAIL_USER
        admin_msg["To"] = MAIL_USER
        admin_msg.set_content(f"""
You received a new contact form submission from the SahuOne website:

👤 Name: {name}
📧 Email: {email}
📝 Subject: {subject}

💬 Message:
{message}
        """)

        # Auto-reply to User
        user_msg = EmailMessage()
        user_msg["Subject"] = "Thank you for contacting SahuOne!"
        user_msg["From"] = "SahuOne <hello@sahuone.com>"
        user_msg["To"] = email
        user_msg.set_content(f"""
Hello {name},

Thank you for reaching out to SahuOne! 🙏
We’ve received your message and our team will get back to you shortly.

If this was a support request, expect a reply within 24–48 hours.

Regards,
✨ SahuOne Team
📍 https://sahuone.com
        """)

        try:
            with smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT) as smtp:
                smtp.login(MAIL_USER, MAIL_PASSWORD)
                smtp.send_message(admin_msg)
                smtp.send_message(user_msg)

            flash("✅ Your message was sent successfully!", "success")

        except Exception as e:
            print("Email Error:", e)
            flash("❌ Something went wrong. Please try again later.", "error")

        return redirect("/thank_you")

    return render_template("connect.html", page_title="Contact SahuOne")

@app.route("/thank_you")
def thank_you():
    return render_template('thank_you.html', page_title="Thank You!")
    
@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html', page_title="portfolio")
    
@app.route("/resume")
def resume():
    return render_template('resume.html', page_title="resume")  

@app.route("/privacy")
def privacy():
    return render_template('privacy.html')

@app.route("/terms")
def terms():
    return render_template('terms.html')
    
@app.route("/documentation")
def documentation():
    return render_template('documentation.html')  

@app.route("/help")
def help():
    return render_template('help.html')

@app.route("/work")
def work():
    return render_template('work.html')
    
@app.route("/careers")
def careers():
    return render_template('careers.html')
    
@app.route("/status")
def status():
    return render_template('status.html')
    
@app.route("/cookies")
def cookies():
    return render_template('cookies.html') 
    
@app.route("/devskysolar")
def devskysolar():
    return render_template('devskysolar.html') 
    
@app.route("/jeevanyatra")
def jeevanyatra():
    return render_template('jeevanyatra.html')     

@app.route('/qr')
def qr():
    return render_template('qr.html')

if __name__ == "__main__":
    app.run(debug=True)
