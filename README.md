# Azure serverless Telegram bot
Deploy and run your Telegram bot on Azure-based serverless architecture. This simple platform will handle bot requests `/start` and `/stop` to register Telegram conversation in a Storage Account blob so that it can be used to send messages to chats.

# How to start
1. (Optional) Get a custom domain. [Freenom](http://www.freenom.com/en/index.html) is a good starting point to obtain a domain for free.
2. Deploy infrastructure on Azure: edit the file `.cicd/parameters/dev.json`, then run a deployment on ARM. You can use Azure CLI or Az Powershell. You will now have a resource group with a Key Vault, a Storage Account, an Azure Function and some other resources.
3. Follow the [instructions](https://core.telegram.org/bots#3-how-do-i-create-a-bot) to create a new Telegram bot and retrieve the bot token.
4. Edit the Azure Function configuration and add an entry `cfg-secret-telegram-bot-token` with the token, or create a secret in the Key Vault called `telegram-bot-token`.
5. Set up the bot to use webhooks on the bot endpoint, you can use the script `setup.py` after editing it. If you don't want to use a certificate, comment out that part.
6. Deploy the Azure Function.

# Run locally
To run locally create a file `local.settings.json` in the `bot` folder. Set it up in this way:
```
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "{CONNECTION_STRING_TO_STORAGE_ACCOUNT}",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobs.BotEndpoint.Disabled": "false",
    "cfg-config-core-mainkeyvault": "az-serverless-bot",
    "cfg-config-core-mainstorage": "az-serverless-bot",
    "cfg-secret-telegram-bot-token": "{TELEGRAM_BOT_TOKEN}"
  }
}
```
Run the Azure Function and use [ngrok](https://ngrok.com/) to obtain a temporary public endpoint that exposes the local endpoint. Update the Telegram bot to send updates accordingly.