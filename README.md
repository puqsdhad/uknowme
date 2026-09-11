<p align="center">
    <a href="https://github.com/puqsdhad/uknowme">
        <img src="https://raw.githubusercontent.com/pyrogram/artwork/master/artwork/pyrogram-logo.png" alt="WVLGram" width="128">
    </a>
    <br>
    <b>Telegram MTProto API Framework for Python (Modified Version)</b>
    <br>
    <a href="https://github.com/puqsdhad/uknowme">
        <b>👉 Repository 👈</b>
    </a>
    <br>
    <br>
    <a href="https://t.me/WannnKW">
        Support
    </a>
</p>

## WVLGram

> **⚠️ WVLGram (Wann Vlife Telegram) adalah modifikasi dari Pyrogram, dan hanya dipergunakan untuk komunitas pribadi.**
>
> **Support & Updates:** [t.me/WannnKW](https://t.me/WannnKW)
>
> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots.
> Support Effect Emoji in chat
> Stabil & Power Full

``` python
from WVLGram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from WVLGram!")


app.run()
```

**WVLGram** is a modern, elegant and asynchronous MTProto API framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot identity (bot API alternative) using Python.

> This project is a modified version of [Pyrogram](https://github.com/pyrogram/pyrogram). All credit for the original
> framework goes to the Pyrogram authors (Copyright (C) 2017-present Dan <https://github.com/delivrance>). WVLGram is
> maintained for private community use only, created by [t.me/WannnKW](https://t.me/WannnKW).

### Support

For support regarding this modified version, please contact: [t.me/WannnKW](https://t.me/WannnKW)

### Key Features

- **Ready**: Install WVLGram with pip and start building your applications right away.
- **Easy**: Makes the Telegram API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by [TgCrypto](https://github.com/pyrogram/tgcrypto), a high-performance cryptography library written in C.
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Telegram's API to execute any official client action and more.

### Installing

``` bash
pip3 install git+https://github.com/puqsdhad/uknowme
```

### Resources

- Modified version updates by [t.me/WannnKW](https://t.me/WannnKW)
