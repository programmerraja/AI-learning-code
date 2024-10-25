import imaplib, os, email  # noqa: E401
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_GEMENI_API_KEY"))

GEMINI_LLM = genai.GenerativeModel("gemini-1.5-flash-001")


def connect_to_inbox():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.getenv("GMAIL_ID"), os.getenv("GMAIL_PASS"))
    mail.select("inbox")
    return mail


def get_latest_email(mail):
    _, message_numbers = mail.search(None, "ALL")
    print(message_numbers)

    latest_email_id = message_numbers[0].split()[-1]

    _, msg_data = mail.fetch(latest_email_id, "(RFC822)")

    email_body = msg_data[0][1]

    message = email.message_from_bytes(email_body)

    return message, latest_email_id


def get_email_content(message):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return message.get_payload(decode=True).decode()


def summarize_email(content):
    response = GEMINI_LLM.generate_content(
        f"Please summarize the following email:\n\n{content}"
    )
    return response.text


def main():
    mail = connect_to_inbox()

    while True:
        message, email_id = get_latest_email(mail)

        print(f"\nFrom: {message['From']}")
        print(f"Subject: {message['Subject']}")

        summarize = input("\nDo you want to summarize this email? (yes/no): ").lower()

        if summarize == "yes":
            content = get_email_content(message)
            summary = summarize_email(content)
            print(f"\nSummary:\n{summary}")

        delete = input("\nDo you want to delete this email? (yes/no): ").lower()
        if delete == "yes":
            mail.store(email_id, "+FLAGS", "\\Deleted")
            mail.expunge()
            print("Email deleted.")

        finish = input("\nDo you want to finish processing emails? (yes/no): ").lower()
        if finish == "yes":
            break

    mail.close()
    mail.logout()


if __name__ == "__main__":
    main()
