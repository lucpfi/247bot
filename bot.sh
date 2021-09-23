#!/usr/bin/env bash

if [[ "$1" == "install" ]]
then
    echo "Installing requirements ..."

    sudo apt update
    sudo apt install python3 python3-pip ffmpeg curl screen -y
    pip3 install discord
    pip3 install discord-py-slash-command
    pip3 install asyncio

    rm botconfig.py

    touch botconfig.py

    echo "Please enter your Bot token and your Application/Client ID. (You must register the Bot application here: https://discord.com/developers/applications, there can you get the Bot Token)"
    read -p "Bot Token: " token
    read -p "Bot Application ID: " applicationID
    echo ""

    echo "Please enter now you spotify Client ID and Client Secret. (you can get it here: https://developer.spotify.com/dashboard/applications)"
    read -p "Spotify Client ID: " clientID
    read -p "Spotify Client Secret: " clientSecret
    echo ""

    echo "Please enter finaly your Guild ID. (To get this you must enable the Developer Mode on your Discord Account and right click on the Server Name you would have this Bot.)"
    read -p "Guild ID: " guildID
    echo ""
    echo "Are this Informations Right?"
    echo "Bot Token: $token"
    echo "Bot Application/Client ID: $applicationID"
    echo "Spotify Client ID: $clientID"
    echo "Spotify Client Secret: $clientSecret"
    echo "Guild ID: $guildID"
    read -p "(yes/no) " confirm
    if [[ "$confirm" == "yes" ]] 
    then
        echo "bot = {'token': '$token'}" >> botconfig.py
        echo "spotify = {'clientID': '$clientID', 'clientSecret': '$clientSecret'}" >> botconfig.py
        echo "guild_ids = [$guildID]" >> botconfig.py

        echo "The Bot is ready! Invite the bot with this url: https://discord.com/api/oauth2/authorize?client_id=$applicationID&permissions=3258002544&scope=bot%20applications.commands"
        echo "Use ./bot start to Start the bot. With ./bot help you can get a list of Available Commands."
    else
        echo "Abborting..."
    fi
elif [[ "$1" == "start" ]]
then
    echo "Starting the Bot..."
    screen -AmdS discord-bot -L python3 main.py
    echo "The bot is in a few seconds Online"
elif [[ "$1" == "stop" ]]
then
    echo "Stopping the Bot..."
    screen -S discord-bot -X quit
    echo "The Bot is stopped"
elif [[ "$1" == "help" ]]
then
    echo "Usage: ./bot [option]"
    echo "install       Install/Reconfigure the Bot"
    echo "start         Starts the Bot as a deamon"
    echo "stop          Stops the Bot"
    echo "help          Show this"
    echo "console       Shows the Console"
elif [[ "$1" == "console" ]]
then
    echo "Entering the Console... Please press ctrl + a d and NOT ctrl + c to leave the console, this Stops the Bot!"
    read -r -p "press any key to continue" -t 5 -n 1 -s
    screen -r discord-bot
fi
