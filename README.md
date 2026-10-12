# not-jagen
A Fire Emblem: Fortune's Weave stats bot written in discord.py.

## Setup
1. Create a `.env` file in the main directory with the token for your Discord application and your Discord account ID:
```
TOKEN=[your token]
OWNER_ID=[your Discord account ID]
```
2. Install the necessary dependencies via command line:
```commandline
python -m pip install -r requirements.txt
```

## Operation
1. Start the bot:
```commandline
python main.py
```

2. Upload the commands to Discord:

Before your commands can be run from the bot, its command list must be synced with Discord's servers.
This is done via a plaintext command, by default assigned to `!sync`.
DM this command to the bot and it will upload its commands to the remote.
You may need to restart your Discord app before the commands become visible on your client.

**You should run the `!sync` command whenever you add or remove a command, or whenever you edit the inputs of a command.**
In general, unless the only changes you have made to a command are **inside the function** (e.g. changing a formula within a command), you should always re-sync.
Otherwise, Discord may not recognize your inputs.
