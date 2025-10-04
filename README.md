# Home-security-system
Smart Home Security System using Raspberry Pi A compact home security setup using Raspberry Pi 3, featuring motion detection, RFID + keypad access, intrusion alerts with buzzer, and camera snapshots sent to a Flask web server.

What this project does:
Monitors door/area with an ultrasonic sensor (presence/distance).
Reads temperature & humidity (DHT11/DHT22).
Controls RFID keys (e.g., RC522) and a matrix keypad for entry.
Sounds a buzzer when a user enters the wrong code/key several times (configurable threshold).
When intrusion is detected or repeated failed attempts occur, the camera captures pictures of the intruder and sends images to a Flask web server (HTTP POST).
Server stores images and can trigger alerts or a dashboard.
