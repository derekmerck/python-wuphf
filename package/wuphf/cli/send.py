import yaml
import click
from pprint import pformat


@click.command(short_help="Send WUPHF message via messenger endpoint")
@click.argument('messenger',   type=click.STRING)
@click.argument('data',        type=click.STRING)
@click.option('target', '-t',  type=click.STRING, help="Optional target, if not using a dedicated messenger")
@click.option('msg_t',  '-m',  type=click.STRING, help="Optional message template")
@click.pass_context
def send(ctx, messenger, data, target, msg_t):
    """"Use MESSENGER endpoint to send DATA"
     \b
     $ wuphf-cli send smpt_messenger "msg_text: Hello 123" \
                     -t test@example.com
    """
    manager = ctx.obj.get('manager')

    ep = manager.get(messenger)
    if not ep:
        click.echo(click.style("No such endpoint {}".format(messenger), fg="red"))
        exit(1)

    click.echo(click.style('Calling endpoint send method', underline=True, bold=True))

    _data = yaml.load(data)
    # print(_data)
    _target = yaml.load(target)
    # print(_target)

    out = ep.send(_data, target=_target, msg_t=msg_t)

    if out:
        click.echo(pformat(out))
        exit(0)
    else:
        click.echo(click.style("No response", fg="red"))
        exit(2)
