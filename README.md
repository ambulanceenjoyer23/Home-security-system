# Home-security-system
Smart Home Security System using Raspberry Pi A compact home security setup using Raspberry Pi 3, featuring motion detection, RFID + keypad access, intrusion alerts with buzzer, and camera snapshots sent to a Flask web server.

What this project does:
------------------------------------------------------------------
Monitors door/area with an ultrasonic sensor (presence/distance).

Reads temperature & humidity (DHT11/DHT22).

Controls RFID keys (e.g., RC522) and a matrix keypad for entry.

Sounds a buzzer when a user enters the wrong code/key several times (configurable threshold).

When intrusion is detected or repeated failed attempts occur, the camera captures pictures of the intruder and sends images to a Flask web server (HTTP POST).

Server stores images and can trigger alerts or a dashboard.


<img width="1920" height="1080" alt="Failed intruder attempt terminal" src="https://github.com/user-attachments/assets/c5154ffd-4f5f-4046-9ddd-e23c4bc03a3f" />
<img width="1920" height="1080" alt="Take RFID user pic" src="https://github.com/user-attachments/assets/77251138-a4d8-45cd-b755-ad7f697c5dbf" />
<img width="1920" height="1080" alt="RFID access" src="https://github.com/user-attachments/assets/bd6fc833-118e-4622-8fee-f981d355d6df" />
<img width="1920" height="1080" alt="AC on and off" src="https://github.com/user-attachments/assets/e49609c4-8251-41e7-a3f3-ec19614d15a8" />
<img width="1920" height="1080" alt="Rotating LED intensity" src="https://github.com/user-attachments/assets/82a1fe06-d1ca-4697-89dc-16b75c9eaecd" />
