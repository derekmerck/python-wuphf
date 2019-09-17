import logging
import yaml
import json
from typing import Union, Mapping
import attr
from crud.abc import Endpoint, Item
from crud.utils import render_template


def check_file_ref(_value):
    if isinstance(_value, str) and _value.startswith("@"):
        try:
            fn = _value[1:]
            with open(fn) as f:
                if fn.endswith(".yaml"):
                    value = yaml.load(f)
                elif fn.endswith(".json"):
                    value = json.loads(f)
                else:
                    value = f.read()
                return value
        except FileNotFoundError:
            logging.warning("WARNING: Inferred file name from {}, but file is missing or misformed!".format(value))
    return _value


@attr.s
class Messenger(Endpoint):

    target = attr.ib(default=None)
    msg_t = attr.ib(default="{{msg_text}}", converter=check_file_ref)
    wrap = attr.ib(default=70)

    # String send
    def _send(self, msg, target, **kwargs):
        raise NotImplementedError

    def get(self, item: Union[Item, Mapping], target=None, msg_t=None, **kwargs):
        if not target:
            target = self.target
        if not target:
            raise ValueError("No target address provided")
        if not msg_t:
            msg_t = self.msg_t
        if not msg_t:
            raise ValueError("No message template provided")

        if isinstance(item, dict):
            data = item
        elif hasattr(item, 'data'):
            data = item.data
        elif hasattr(item, 'meta'):
            data = item.meta
        else:
            raise TypeError("Cannot convert {} to mapping")

        if hasattr(self, "from_addr"):
            data["from_addr"] = self.from_addr

        msg = render_template(msg_t, target=target, **data, **kwargs )
        return msg

    # Item send with template
    def send(self, item: Union[Item, Mapping], target=None, msg_t=None, dryrun=False, **kwargs):
        msg = self.get(item, target, msg_t, **kwargs)
        if not dryrun:
            self._send(msg, target, **kwargs)
        else:
            logger = logging.getLogger(self.name)
            logger.info("Dry run message is:\n{}".format(msg))
