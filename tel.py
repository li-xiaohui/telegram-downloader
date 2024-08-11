import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
import pandas as pd
from util import *
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
import os
from constants import *

## output dir
dir_name = f'output {datetime.now().strftime("%Y-%m-%d")}'
##create dir if not exists
Path(dir_name).mkdir(parents=True, exist_ok=True)

# Create a Telegram client with the specified API ID, API hash and phone number
phone_number = os.getenv("phone_number")
client = TelegramClient(phone_number, 
                        os.getenv('api_id'), 
                        os.getenv("api_hash"))

async def get_group_messages():
    await client.start()
    
    # Check if the user is already authorized, otherwise prompt the user to authorize the client
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Enter the code: '))

    for group_name, group_id in CHANNEL_NAMES.items():
        print(f'downloading from {group_name} ...')
        # Get the ID of the specified group
        group=None
        try:
            group = await client.get_entity(group_id)
        except:
            print(f'Exception when downloading from {group_name}')
            pass
        if group:
            date_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            since_date = date_today - timedelta(days=7)
            data = []
            # below commented code is used for  specified time range
            async for message in client.iter_messages(group, min_id=1):
                # print('sender_id: ', message.sender_id, '; msg date: ', message.date) 
                if str(message.date) < str(since_date):
                # if message.date.strftime('%Y-%m-%d') < '2024-03-31':
                    break
                data.append([message.sender_id, message.text, message.date, message.id, message.post_author, message.views, message.peer_id.channel_id ])
                
            print('data size: ', len(data))
            ## save messages to df
            df = pd.DataFrame(data, columns=["sender_id", "text", "date", "id",  
                                            "post_author", "views", 
                                            "channel_id" ])
            # Remove timezone from columns
            df['date'] = df['date'].dt.tz_convert('Asia/Singapore').dt.tz_localize(None)
            
            ## add group_name
            df.insert(0 , 'channel', group_name)
            
            df.to_excel(f"{dir_name}/{group_name} {date_today.strftime('%Y-%m-%d')}.xlsx", index=False)
    
asyncio.run(get_group_messages())

## zip file
output_filename = f'{dir_name}.zip'
recipient_email = os.getenv("recipient_email")

subject = "Tel data"
body = "with attachment"

print('Zipping folder ...')
## Now zip file 
zip_folder(dir_name, dir_name)
print(f'Done!\nSending email to {recipient_email}...')

## send email
send_mail_with_gmail(
    os.getenv('gmail_username'),
    os.getenv('gmail_pwd'),
    recipient_email, 
    subject, 
    body, 
    output_filename)
print('Done!')