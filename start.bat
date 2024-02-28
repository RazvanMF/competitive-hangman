@echo off
echo COMPETITIVE HANGMAN
echo.
echo 1. Server-side Program
echo 2. Client-side Program
echo 3. Singleplayer
echo.
set /p choice= "Please Select one of the above options: " 
if %choice%==1 (
	echo Hold on...
	echo Getting IPv4 address...
	::ipconfig /all | wsl grep -A8 "Wireless LAN adapter Wi-Fi" | wsl grep "IPv4" | wsl grep -o -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"
	netsh interface ip show config name="Wi-Fi" | findstr "IP Address"
	echo Please make sure the clients and the server use this IP address.
	echo.
	pause

	cls
	python server.py
)
if %choice%==2 (
	cls
	python client.py
)
if %choice%==3 (
	cls
	python singleplayer.py
)
pause