import logging
from enum import Enum
from typing import Mapping
import time
import attr
from crud.abc import Endpoint, DaemonMixin, Serializable
from ..abc.messenger import check_file_ref
from ..endpoints import SmtpMessenger, EmailSMSMessenger, SlackMessenger


@attr.s
class Message:

    data = attr.ib()
    channels = attr.ib(default=None)


class Transport(Enum):
    EMAIL = "email"
    SMS   = "sms"
    PHONE = "phone"
    SLACK = "slack"


@attr.s
class Subscriber:

    name = attr.ib(default=None)
    role = attr.ib(default=None)
    channels = attr.ib(factory=list)

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
            result[Transport.EMAIL] = {"target":   self.email}
        if self.sms:
            result[Transport.SMS]   = {"target":   self.sms,
                                       "carrier":  self.carrier}
        if self.slack:
            result[Transport.SLACK] = {"token":    self.slack}
        if self.phone:
            result[Transport.PHONE] = {"target":   self.phone}
        return result

    def listening(self, channels):
        if "all" in channels:
            return True
        for c in ["all", *channels]:
            if c in self.channels:
                return True


@attr.s
class Dispatcher(Endpoint, DaemonMixin):

    subscriptions_desc = attr.ib(default=None, type=Mapping, repr=False, convert=check_file_ref)
    subscriptions = attr.ib(type=list)
    @subscriptions.default
    def create_subscriptions(self):
        if self.subscriptions_desc:
            subscriptions = []
            for item in self.subscriptions_desc:
                channels = [item["channel"]]
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

    def put(self, data, channels=None, msg_t=None):
        logger = logging.getLogger(self.__class__.__name__)
        print("Putting in queue (test)")
        logger.debug("Putting item in queue")
        message = Message(data=data, channels=channels)
        self.job_queue.put(message)
        logger.debug("Queue is empty ({})".format(self.job_queue.empty()))

    def handle_item(self, item, dryrun=False):
        logger = logging.getLogger(self.__class__.__name__)
        logger.debug("Handling item")
        for subscriber in self.subscriptions:
            if subscriber.listening(item.channels):
                print("{} received {}".format(subscriber.name, item.data))
                transports = subscriber.get_transports()
                for k, v in transports.items():
                    print(v)
                    ep = self.messengers.get(k)
                    if ep:
                        data = {
                            **item.data,
                            "recipient": subscriber
                        }
                        ep.send(data, **v, dryrun=dryrun)
                    else:
                        print("No relay available for {}: {}".format(k, v))

    def run(self, dryrun=False):
        while True:
            self.handle_queue()
            time.sleep(1.0)


#Dispatcher.register()
Serializable.Factory.registry["Dispatcher"] = Dispatcher
