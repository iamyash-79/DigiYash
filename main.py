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
ADMIN_EMAIL = 'yashcybercafeofficial@gmail.com'
ADMIN_APP_PASSWORD = 'jgwujcylyefeaefz'  # App Password generated from Google

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
    
@app.route("/enrollment")
def enrollment():
    return render_template('enrollment.html', page_title="enrollment")   
    
@app.route("/excel")
def excel():
    return render_template('excel.html', page_title="excel") 
    
@app.route('/split', methods=['POST'])
def split_file():
    file = request.files['file']
    if not file:
        return "❌ कोई फ़ाइल अपलोड नहीं हुई!"

    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # पुरानी uploads साफ करो
    for f in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, f))

    # फ़ाइल पढ़ो
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # कॉलम पहचानो
    possible_cols = ['College Code', 'college_code', 'COLLEGECODE', 'College_Code']
    found_col = next((col for col in possible_cols if col in df.columns), None)
    if not found_col:
        return "❌ Excel/CSV में 'College Code' कॉलम नहीं मिला!"

    # URL prefix
    url_prefix = "https://d2xe8shibzpjog.cloudfront.net/Guideline/smkv/"

    # Split and save Excel files
    codes = df[found_col].dropna().unique()
    for code in codes:
        sub_df = df[df[found_col] == code]

        # Real URL (exact format for display)
        file_url = f"{url_prefix}{code}.xlsx"

        # Safe filename for saving
        safe_name = urllib.parse.quote(file_url, safe='')  # encode full URL safely
        file_path = os.path.join(UPLOAD_FOLDER, f"{safe_name}.xlsx")

        sub_df.to_excel(file_path, index=False)

    # ZIP बनाओ
    zip_path = os.path.join(UPLOAD_FOLDER, "split_files.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for f in os.listdir(UPLOAD_FOLDER):
            if f.endswith(".xlsx") and f != "split_files.zip":
                zipf.write(os.path.join(UPLOAD_FOLDER, f), arcname=f)

    return send_file(zip_path, as_attachment=True)

@app.route('/download_zip')
def download_zip():
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    zip_path = os.path.join(UPLOAD_FOLDER, 'split_files.zip')

    # remove existing zip if any
    if os.path.exists(zip_path):
        os.remove(zip_path)

    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for fname in os.listdir(UPLOAD_FOLDER):
            # skip the zip itself and non-xlsx if you want
            if not fname.endswith('.xlsx') or fname == 'split_files.zip':
                continue

            full_path = os.path.join(UPLOAD_FOLDER, fname)

            # fname is something like: "https%3A%2F%2Fd2xe8...%2F101.xlsx.xlsx"
            # remove the extra .xlsx suffix that you might have appended earlier
            base_no_ext = fname
            if base_no_ext.lower().endswith('.xlsx'):
                base_no_ext = base_no_ext[:-5]   # remove ".xlsx"

            # decode percent-encoding
            decoded = urllib.parse.unquote(base_no_ext)

            # OPTION B: keep the whole decoded string as filename but make it filesystem-safe
            safe_name = decoded.replace('://', '___').replace(':', '___').replace('//', '_')
            # replace any forward-slash with underscore so it doesn't become a path inside the zip
            safe_name = safe_name.replace('/', '_').replace('\\', '_')
            # finally ensure .xlsx extension
            if not safe_name.lower().endswith('.xlsx'):
                safe_name = safe_name + '.xlsx'

            # now write into zip with the safe filename (no directories)
            zipf.write(full_path, arcname=safe_name)

    # send zip
    return send_file(zip_path, as_attachment=True)
if __name__ == "__main__":
    app.run(debug=True)
