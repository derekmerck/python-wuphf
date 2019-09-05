from queue import Queue
from enum import Enum
from typing import Mapping
import time
import attr
from crud.abc import Endpoint
from ..endpoints import SmtpMessenger, EmailSMSMessenger, TwilioMessenger, SlackMessenger


def all_lower(_list):
    result = []
    for item in _list:
        result.append(item.lower())
    return result


@attr.s
class Message:

    data = attr.ib()
    channels = attr.ib(default=None, convert=all_lower)


class Transport(Enum):
    EMAIL = "email"
    SMS   = "sms"
    PHONE = "phone"
    SLACK = "slack"


@attr.s
class Subscriber:

    name = attr.ib(default=None)
    role = attr.ib(default=None)
    channels = attr.ib(factory=list, convert=all_lower)

    # Transports
    email = attr.ib(default=None)
    sms   = attr.ib(default=None)
    carrier = attr.ib(default=None)
    slack = attr.ib(default=None)
    phone = attr.ib(default=None)

    transports = attr.ib(init=False)
    @transports.default
    def get_transports(self):
        result = {}
        if self.email:
            result[Transport.EMAIL] = {"target": self.email}
        if self.sms:
            result[Transport.SMS]   = {"target":   self.sms,
                                       "carrier":  self.carrier}
        if self.slack:
            result[Transport.SLACK] = {"token":    self.slack}
        if self.phone:
            result[Transport.PHONE] = {"target":   self.phone}
        return result

    def listening(self, channels):
        for c in ["all", *channels]:
            if c in self.channels:
                return True


@attr.s
class Dispatcher(Endpoint):

    message_queue = attr.ib(init=False, factory=Queue)

    subscriptions_desc = attr.ib(default=None, type=Mapping)
    subscriptions = attr.ib(type=list)
    @subscriptions.default
    def create_subscriptions(self):
        if self.subscriptions_desc:
            subscriptions = []
            for item in self.subscriptions_desc:
                channels = item["channel"]
                for subscriber in item["subscribers"]:
                    subscriptions.append(Subscriber(**subscriber, channels=channels))
            return subscriptions

    smtp_messenger_desc = attr.ib(default=None, type=Mapping)
    smtp_messenger = attr.ib(type=SmtpMessenger)
    @smtp_messenger.default
    def create_smtp_messenger(self):
        if self.smtp_messenger_desc:
            return SmtpMessenger(**self.smtp_messenger_desc)

    sms_messenger = attr.ib(default=None, type=EmailSMSMessenger)
    slack_messenger = attr.ib(default=None, type=SlackMessenger)
    # twilio_messenger = attr.ib(default=None, type=TwilioMessenger)

    messengers = attr.ib(init=False)
    @messengers.default
    def init_messengers(self):
        return {
            Transport.EMAIL: self.smtp_messenger,
            Transport.SMS:   self.sms_messenger,
            Transport.SLACK: self.slack_messenger
        }

    def add_subscriber(self, subscriber):
        self.subscriptions.append(Subscriber(**subscriber))

    def put(self, data, channels=None):
        message = Message(data=data, channels=channels)
        self.message_queue.put(message)

    def handle_queue(self, dryrun=False):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            for subscriber in self.subscriptions:
                if subscriber.listening(message.channels):
                    print("{} received {}".format(subscriber.name, message.data))
                    transports = subscriber.get_transports()
                    for k, v in transports.items():
                        print(v)
                        ep = self.messengers.get(k)
                        if ep:
                            ep.send(message.data, **v, dryrun=dryrun)
                        else:
                            print("No relay available for {}: {}".format(k, v))

        # Only send 1 email, with all to_addrs together
        # Only submit to slack channel once
        # Send twilio phone message to all numbers (only 1nce each)

    def run(self):
        while True:
            self.handle_queue()
            time.sleep(1.0)
