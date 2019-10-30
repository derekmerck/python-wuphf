import attr
from typing import List, Mapping
import yaml
import logging
from collections import deque
from pprint import pprint
from crud.abc import Endpoint, Serializable
from wuphf.abc import Messenger
from wuphf.endpoints import SmtpMessenger

@attr.s
class MyDispatcher(Endpoint):

    channels_desc = attr.ib(type=Mapping, default=None)
    channels = attr.ib(type=Mapping)

    @attr.s
    class Channel:
        tag = attr.ib(type=str)
        trial = attr.ib(type=str)
        site = attr.ib(type=str)

    def add_channel(self, tag, desc):
        c = self.Channel(**desc, tag=tag)
        self.channels[tag] = c

    @channels.default
    def setup_channels(self):
        channels = {}
        for tag, desc in self.channels_desc.items():
            c = self.Channel(tag=tag, **desc)
            channels[tag] = c
        return channels

    def clean_channels(self, requested_channels):
        clean_channels = []
        for c in requested_channels:
            if c in self.channels:
                clean_channels.append(c)
            else:
                for cc in self.channels.keys():
                    if c in cc:
                        clean_channels.append(cc)

        if clean_channels:
            return  clean_channels
        else:
            logger = logging.getLogger()
            logger.warning("No valid channels in {}".format(requested_channels))
            return []

    @attr.s
    class Subscriber:
        name = attr.ib()
        listening = attr.ib(factory=list)
        email = attr.ib(default=None)

    subscribers_desc = attr.ib(type=Mapping, default=None)
    subscribers = attr.ib(type=List)

    def add_subscriber(self, subscriber_desc):
        s = self.Subscriber(**subscriber_desc)
        s.listening = self.clean_channels(s.listening)
        self.subscribers.append(s)

    @subscribers.default
    def setup_subscribers(self):
        subscribers = []
        for desc in self.subscribers_desc:
            s = self.Subscriber(**desc)
            s.listening = self.clean_channels(s.listening)
            subscribers.append(s)
        return subscribers

    def subscribers_for(self, channels: List):
        _channels = self.clean_channels(channels)
        logger = logging.getLogger()
        logger.debug("Found matching channels: {}".format(_channels))
        res = []
        for c in _channels:
            for s in self.subscribers:
                if c in s.listening:
                    if s not in [_s for _s,_c in res]:
                        res.append((s,c))
                        logger.debug("Found subscriber '{}' on #{}".format(s.name, c))
        return res


    queue = attr.ib(factory=deque, init=False)

    def put(self, item: Mapping, channels: List):
        for s, c in self.subscribers_for(channels):
            _item = {"item": item,
                     "channel": attr.asdict(self.channels[c]),
                     "recipient": attr.asdict(s)}
            self.queue.append((_item, s))

    messengers = attr.ib(factory=dict, init=False)

    def add_messenger(self, mtype: str, messenger: Messenger):
        self.messengers[mtype] = messenger

    def messenger_for(self, s: Subscriber):
        if s.email:
            return self.messengers["email"], s.email
        raise TypeError("No available messenger!")

    def handle_item(self, item: tuple, dryrun=False):
        _item, sub = item
        messenger, dest = self.messenger_for(sub)
        if not dryrun:
            messenger.send(_item, dest)
        else:
            logging.info("DRYRUN: item {} sent to {}".format(_item["item"], dest))
            logging.info(messenger.get(_item, dest))

    def peek_item(self, item: tuple):
        _item, sub = item
        messenger, dest = self.messenger_for(sub)
        return messenger.get(_item, dest)

    def handle_queue(self, dryrun=False):
        while len(self.queue) > 0:
            item: tuple = self.queue.pop()
            self.handle_item(item, dryrun=dryrun)

    def peek_queue(self):
        rv = []
        for item in self.queue:
            rv.append( self.peek_item(item) )
        return rv


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    with open("channels.yaml") as f:
        ch_d, sub_d = yaml.load_all(f)
    disp = MyDispatcher(channels_desc=ch_d, subscribers_desc=sub_d)

    disp.add_messenger("email", SmtpMessenger())

    pprint(disp.channels)
    pprint(disp.subscribers)

    print("hobit or testing")
    s = disp.subscribers_for(["hobit", "testing"])
    pprint(s)

    print("hobit-duke")
    s = disp.subscribers_for(["hobit-duke"])
    pprint(s)

    print("duke")
    s = disp.subscribers_for(["duke"])
    pprint(s)

    print("detroit")
    s = disp.subscribers_for(["detroit"])
    pprint(s)

    disp.put({"value": 100}, ["detroit"])

    disp.handle_queue()

Serializable.Factory.registry["Dispatcher"] = MyDispatcher