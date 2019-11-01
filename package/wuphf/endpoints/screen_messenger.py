from pprint import pprint
import attr

@attr.s
class ScreenMessenger:

    def send(self, item, **kwargs):
        pprint(item)

