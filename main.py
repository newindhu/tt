from telethon import TelegramClient, events, errors
import asyncio

# Your API credentials
api_id = '28170741'  # Replace with your API ID
api_hash = '0f04efb7ef30a5f565eb540483729548'  # Replace with your API Hash

# Your phone number for user account authentication
phone_number = '+94 77 015 2585'  # Replace with your phone number

# Target chat (your channel) where videos will be forwarded
target_chat = 'HUTHTHI7'  # Replace with the target channel username or ID

# Initialize the Telegram client using user account (not bot token)
client = TelegramClient('forward_user_session', api_id, api_hash)

# Variable to store the source chat provided by the user
source_chat_link = None

# Counter to track the total number of MP4 videos forwarded
total_videos_forwarded = 0

@client.on(events.NewMessage)
async def handle_message(event):
    """
    Handles incoming messages.
    - If a source channel link is sent, sets the source chat.
    - Starts forwarding videos from the source channel to the target channel.
    """
    global source_chat_link

    # Get the text from the incoming message
    message_text = event.raw_text.strip()

    # Check if the message is a Telegram channel link or username
    if message_text.startswith('https://t.me/') or message_text.startswith('@'):
        source_chat_link = message_text  # Set the source chat link
        await event.reply(f"Source channel set to: {source_chat_link}")
        print(f"Source channel updated: {source_chat_link}")

        # Start forwarding videos from the source chat
        await forward_videos_from_source()

async def forward_videos_from_source():
    """
    Forwards only MP4 videos from the source chat to the target chat.
    This function will forward MP4 videos once and then stop until a new source channel is provided.
    """
    global source_chat_link, total_videos_forwarded

    if not source_chat_link:
        print("No source chat set. Waiting for input...")
        return

    print(f"Starting to forward MP4 videos from {source_chat_link} to {target_chat}...")
    try:
        # Iterate through messages in the source chat
        async for message in client.iter_messages(source_chat_link, reverse=True):
            # Check if the message contains a video and if it's an MP4 file
            if message.video and message.video.mime_type == "video/mp4":  
                try:
                    # Forward the MP4 video to the target chat
                    await client.send_file(target_chat, message.video)
                    total_videos_forwarded += 1  # Increment the counter
                    print(f"Forwarded MP4 video: {message.video.id}")
                    # Print the total number of videos forwarded in real-time
                    print(f"Total videos forwarded so far: {total_videos_forwarded}")
                except errors.FloodWaitError as e:
                    print(f"Flood wait: Waiting {e.seconds} seconds...")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    print(f"Error while forwarding MP4 video: {e}")

                # Optional: Add a small delay to avoid hitting rate limits
                await asyncio.sleep(0.5)
            elif message.document and message.document.mime_type == "image/gif":
                # Skip GIFs (based on mime_type "image/gif")
                print(f"Skipped GIF message: {message.id}")
            elif message.sticker:
                # Skip Stickers
                print(f"Skipped Sticker message: {message.id}")
            else:
                # Skip non-video, non-GIF, and non-sticker messages
                print(f"Skipped message: {message.id} (Not an MP4 video, GIF, or Sticker)")

        print(f"Finished forwarding MP4 videos. Total videos forwarded: {total_videos_forwarded}")

    except errors.ChatAdminRequiredError:
        print("User lacks admin permissions in the source or target chat.")
    except errors.FloodWaitError as e:
        print(f"Flood wait error: Waiting {e.seconds} seconds...")
        await asyncio.sleep(e.seconds)
    except errors.RPCError as e:
        print(f"RPC error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Run the bot
if __name__ == "__main__":
    print("Telegram MP4 video forward bot is running...")
    # Authenticate the user account by phone number
    client.start(phone=phone_number)
    # Run the bot and handle messages continuously
    client.run_until_disconnected()
