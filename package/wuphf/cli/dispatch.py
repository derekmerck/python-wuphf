import yaml
import click
from pprint import pformat


@click.command(short_help="Dispatch a WUPHF message to subscribers via dispatcher endpoint")
@click.argument('dispatcher',  type=click.STRING)
@click.argument('data',        type=click.STRING)
@click.argument('channel',     type=click.STRING)
@click.pass_context
def dispatch(ctx, dispatcher, data, channel):
    """"Use DISPATCHER endpoint to send DATA to a #CHANNEL"
     \b
     $ wuphf-cli dispatch dispatcher "msg_text: Hello 123" #project/site1
    """
    manager = ctx.obj.get('manager')

    ep = manager.get(dispatcher)
    if not ep:
        click.echo(click.style("No such endpoint {}".format(dispatcher), fg="red"))
        exit(1)

    _data = yaml.load(data)
    _channel = channel[1:] if channel.startswith('#') else channel
    print(_data)

    click.echo(click.style('Calling endpoint put({}) method'.format(_channel), underline=True, bold=True))
    out = ep.put(_data, channels=[_channel])

    click.echo(click.style('Running daemon queue', underline=True, bold=True))
    out = ep.handle_queue()
