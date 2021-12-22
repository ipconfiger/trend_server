import click
import asyncio
from authorization import create_account, account_list, delete_account


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")


@cli.command()
@click.argument('login_id')
@click.argument('password')
def new_account(login_id, password):
    async def main():
        await create_account(login_id, password)
        click.echo('done')
    asyncio.run(main())


@cli.command()
def list_account():
    async def main():
        await account_list()
    asyncio.run(main())


@cli.command()
@click.argument('login_id')
def del_account(login_id):
    delete_account(login_id)
    click.echo('done')
    click.echo('rest account is below:')
    for ac in account_list():
        click.echo(f'{ac}')


if __name__ == "__main__":
    cli()