import pandas as pd
import mysql.connector
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import schedule
import time

db_config = {
    'user': 'isa_user',
    'password': '4-]8sd51D£A6',
    'host': 'tp-vendor-db.ch6c0kme2q7u.ap-south-1.rds.amazonaws.com',
    'database': 'isa_logistics',
    'port': 3306
}

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "aditya.choudhary@isalogistics.in"
SENDER_PASSWORD = "ldpq yrck kgyz hdxc"
COMPANY_DOMAIN = "isalogistics.in"
GREETING_IMAGE_PATH = 'Final.PNG'

def get_customer_birthdays():
    conn = mysql.connector.connect(**db_config)
    query = """
    SELECT customer_name, email, birthday
    FROM customer_relationship_master
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def send_birthday_email(customer_name, recipient_email, image_path=GREETING_IMAGE_PATH):
    try:
        msg = MIMEMultipart('related')
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f"Happy Birthday {customer_name} 🎉🎂!"
        
        html_body = f"""
        <html>
            <head>
                <link href="https://fonts.googleapis.com/css2?family=Glacial+Indifference&display=swap" rel="stylesheet">
            </head>
            <body style="font-family: 'Glacial Indifference', Arial, sans-serif;">
                <p style="text-align: center; font-size: 24px; font-weight: bold; color: #4d222f; margin-bottom: 20px;">
                    Dear {customer_name}
                </p>
                <div style="text-align: center; margin: 20px 0;">
                    <img src="cid:birthday_image" alt="Birthday Greeting" style="max-width:500px; height:auto;"/>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        
        with open(image_path, 'rb') as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<birthday_image>')
            img.add_header('Content-Disposition', 'inline', filename=image_path)
            msg.attach(img)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to {customer_name} ({recipient_email})")
    except Exception as e:
        print(f"❌ Failed to send email to {customer_name}: {e}")

# ------------------------
# Main Logic
# ------------------------
def main():
    df_customers = get_customer_birthdays()
    df_customers['birthday'] = pd.to_datetime(df_customers['birthday'], errors='coerce')
    
    today = datetime.today()
    birthday_today = df_customers[
        (df_customers['birthday'].dt.day == today.day) &
        (df_customers['birthday'].dt.month == today.month)
    ]
    
    if birthday_today.empty:
        print("No birthdays today 🎈")
    else:
        print(f"Found {len(birthday_today)} birthday(s) today!")
        for _, row in birthday_today.iterrows():
            send_birthday_email(row['customer_name'], row['email'])

# ------------------------
# Schedule the Job
# ------------------------
# Set the time you want the script to run daily, e.g., "09:00"
schedule.every().day.at("12:02").do(main)

print("🎉 Birthday Email Scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(60)