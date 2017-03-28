import aiohttp, asyncio, argparse, os, sys

__author__ = "Alan Baumgartner"

def get_usernames(inputfile):
    #Gets usernames to check from a file
    try:
        with open(inputfile, "r") as f:
            usernames = f.read().split("\n")
            return usernames
    except:
        sys.exit(str(inputfile) + ' does not exists')

def save_username(username, outputfile):
    #Saves available usernames
    with open(outputfile, "a") as a:
        a.write(username+'\n')

async def check_usernames(username, sem, session, loop=None):
    #Checks username availability
    async with sem:
        try:
            async with session.get(URL.format(username)) as resp:
                text = await resp.text()
                if "Sorry, that page doesn’t exist!" in text:
                    save_username(username, outputfile)
        except Exception:
            print(Exception)

async def start_check(conns=50, loop=None):
    #Packs all usernames into a tasklist
    sem = asyncio.BoundedSemaphore(conns)
    async with aiohttp.ClientSession(loop=loop) as session:
        usernames = get_usernames(inputfile)
        tasks = [check_usernames(username, sem, session, loop=loop) for username in usernames]
        await asyncio.gather(*tasks)

def main():
    #Starts the loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_check())
    finally:
        loop.close()

if __name__ == "__main__":
    #Command line parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest='inputfile', action="store")
    parser.add_argument("-o", dest='outputfile', action="store")
    args = parser.parse_args()

    #Assign command line values to variables
    inputfile = args.inputfile
    outputfile = args.outputfile

    #Global constants
    URL = 'https://www.twitter.com/{}'

    if os.path.exists(outputfile):
        #Clears output files
        with open(outputfile, "w") as a:
            print('Output file cleared.')

    #Starts check
    main()