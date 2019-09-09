import logging
import smtplib
import attr
from ..abc import Messenger
from crud.abc import Serializable

sample_msg = """
To: {{ target }}
From: {{ from_addr }}
Subject: Sample WUPHF generated at {{ now() }}.

The WUPHF message is: "{{ msg_text }}"
"""


@attr.s
class SmtpMessenger(Messenger):

    host = attr.ib(default="smtp.example.com")
    port = attr.ib(default=22)
    user = attr.ib(default="admin")
    password = attr.ib(default="passw0rd!")
    tls = attr.ib(default=False)

    from_addr = attr.ib()
    @from_addr.default
    def set_from_addr(self):
        return "{}@{}".format(self.user, self.host)

    class gateway(object):
        def __init__(self, host, port=22, user=None, password=None, tls=False):
            self.gateway = smtplib.SMTP(host, port)
            if tls:
                self.gateway.starttls()
            if user:
                self.gateway.login(user, password)
            self.gateway.set_debuglevel(1)

        def __enter__(self):
            return self.gateway

        def __exit__(self, type, value, traceback):
            self.gateway.close()

    def check(self):
        with self.gateway(self.host, self.port, self.user, self.password, self.tls) as g:
            g.helo()

    def _send(self, msg, to_addrs):

        logger = logging.getLogger(self.name)
        logger.info("Sending message via SMTP connector:\n{}".format(msg))

        with self.gateway(self.host, self.port, self.user, self.password, self.tls) as g:
            g.sendmail(self.from_addr, to_addrs, msg.encode(encoding='UTF-8'))


Serializable.Factory.registry["SmtpMessenger"] = SmtpMessenger
