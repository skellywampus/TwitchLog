# TwitchLog

TwitchLog is a compiled Python application that allows you to monitor chat messages from a specified Twitch streamer's channel. The chat messages are logged into a CSV file with the username, timestamp, and message content.

## Features

- Monitor chat messages from any Twitch streamer's channel.
- Log chat messages into a CSV file.
- Simple and easy-to-use graphical user interface (GUI).

## Requirements

- Twitch Account
- Web Browser

## Usage

1. **Run the application**
	
2. **Log In**:
    - Enter your Twitch username when prompted.
    - The application will open the OAuth token generator page in your default web browser. Obtain the OAuth token from the page.
    - Enter the OAuth token in the password prompt.

3. **Enter the Streamer's Name**:
    - Type the name of the Twitch streamer whose chat you want to monitor in the "Streamer Name" field.

4. **Start the Service**:
    - Click the "Start Service" button to begin monitoring the chat.
    - Chat messages will be logged into a CSV file named after the streamer in the `~/Documents/Twitch_Chats` directory.

5. **Stop the Service**:
    - Click the "Stop Service" button to stop monitoring the chat.

6. **Log Out**:
    - Click the "Log Out" button to log out from your Twitch account.

7. **Close the Application**:
    - Close the application window to exit the program.

## Notes

- A new OAuth token is required each time you run the application.
- Ensure you have a stable internet connection while using the application to monitor Twitch chat.
- DO NOT open the output file while the service is active. It will break the service until you stop and start it again.
