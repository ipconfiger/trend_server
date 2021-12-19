# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import asyncio

from utilities.okex_listsener import private_main, listen_public, ExecInstruments, ExecTickers, public_main


def main():
    asyncio.get_event_loop().run_until_complete(public_main())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
