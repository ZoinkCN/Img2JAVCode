from telethon.sync import TelegramClient, events

api_id = 1371065
api_hash = 'b20dccde2f9d07fb3a0c50d8ec23f24b'
with TelegramClient('zoink', api_id, api_hash) as client:
    client.send_message('me', 'Hello, myself!')
    print(client.download_profile_photo('me'))


    @client.on(events.NewMessage(pattern='(?i).*Hello'))
    async def handler(event):
        await event.reply('Hey!')


    client.run_until_disconnected()
