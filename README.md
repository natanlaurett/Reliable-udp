# Reliable-udp
Implementation of a server-client application with reliable UDP connection.

Some known issues on current implementation (ocasional bugs, when packet loss simulation in set True):
- Already acknolwedged packets included again on ack waiting list, making the server enter in a loop
- Client fails to decode the received json, despite having the server data. Probably some special character issue
