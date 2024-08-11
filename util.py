def send_mail_with_gmail(recipient_email, subject, body_text, attachment_name=None):
    """
    Sends an email using Gmail with optional attachment.

    Args:
    recipient_email (str): The email address of the recipient
    subject (str): The subject of the email
    body_text (str): The body text of the email
    attachment_name (str, optional): The name of the attachment file

    Example:
    send_mail_with_gmail('example@email.com', 'Test email', 'This is a test email', 'file.txt')
    """
    import smtplib
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    ## fill up with your Gmail 
    sender_email = ""
    sender_password = ""

    with open(attachment_name, "rb") as attachment_file:
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(attachment_file.read())
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f"attachment; filename= {attachment_name}",
    )

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    html_part = MIMEText(body_text, 'html')
    message.attach(html_part)
    message.attach(attachment)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())


def zip_folder(dir_name, output_filename):
    """
    Zips a specified directory into a new zip file.

    Parameters:
    dir_name (str): The name of the directory to be zipped.
    output_filename (str): The name of the output zip file.

    Returns:
    None
    """
    import shutil
    # Using Shutil to Zip a Directory
    shutil.make_archive(output_filename, 'zip', dir_name)