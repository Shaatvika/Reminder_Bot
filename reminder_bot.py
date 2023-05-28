from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import datetime
import sched
import time
from twilio.rest import Client
import threading

acc_sid = "ACab30051678ec555478046d7120d8309c"
acc_token = "7fecb5ce482fe679b520fd379859b0e6"
twil_num = "+14155238886"

app = Flask(__name__)
scheduler = sched.scheduler(time.time, time.sleep)
tasks = {}


def send_reminder(task):
    print("Called")
    client = Client(acc_sid, acc_token)

    messageBody = f"Reminder: {task}"
    recipient_number = '+917975906330'

    message = client.messages.create(
        body=messageBody,
        from_=f'whatsapp:{twil_num}',
        to=f'whatsapp:{recipient_number}'
    )

    print(f"Reminder sent to {recipient_number}. Message SID: {message.sid}")


def schedule_task(task):
    print("Scheduled")
    scheduled_time = datetime.datetime.strptime(task['time'], "%Y-%m-%d %H:%M")
    scheduler.enterabs(scheduled_time.timestamp(), 1, send_reminder, (task['task'],))


@app.route("/incoming", methods=["POST"])
def incoming_message():
    message_body = request.form.get("Body")
    sender_number = request.form.get("From")
    response = MessagingResponse()

    if message_body.lower() == "start":
        response.message("Welcome to the reminder bot! To set a reminder, send a message in the following format:\n"
                         "<task>,<time>\n"
                         "For example:\n"
                         "Water the plants,2023-05-28 11:00")
    else:
        parts = message_body.split(",")
        if len(parts) == 2:
            task = {
                'task': parts[0].strip(),
                'time': parts[1].strip()
            }
            tasks[sender_number] = task
            schedule_task(task)
            response.message(f"Reminder set for task: {task['task']}")
        else:
            response.message("Invalid format. Please use the following format:\n"
                             "<task>,<time>")

    return str(response)


def run_scheduler():
    while True:
        scheduler.run(blocking=True)


if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()
    app.run()
    
    