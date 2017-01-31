Principles of Cryptography - Project Synopsis (Secured Audio Conferencing)
===

Team members:
    Asparsh Kumar,
    Soorya Annadurai

Abstract:
---
In today’s world, communications form an integral part of many world applications, from social connectivity, to military strategy, to quick-response healthcare. However, more often than not, a lack of communications security in such critical applications can prove disastrous. This form of security also demands real-time applications, to prevent latency/delay in real-time applications.

To mitigate such issues, we propose an application of cryptographic concepts onto a dynamic audio stream – analogous to walkie-talkies, or mobile communications. However, unlike mobile phones, we do not require a centralized server/network/routing mechanism, such as telecom companies like Verizon, AT&T, and Airtel. And unlike commercial walkie-talkie systems, we provide a dynamically encrypted stream of data through the communication medium which is invulnerable to man-in-the-middle attacks. And unlike military-grade walkie-talkie systems, we do not require a predefined key which, if leaked, leaves the entire military communication system compromised. Such disastrous situations can arise if any physical communications device is stolen, as was frequently observed during World War 2. To this measure, we implement dynamic key exchanges before and during communications at regular intervals. We also propose an authentication mechanism to prevent masquerading attacks during or before the actual key exchange. And such key exchanges will be capable of including more than 2 parties, so as to simulate a broadcast/conference environment.

In summary, we plan to implement a secured conferencing communications medium that prevents masqueraders and middle-man attacks. For the scope of the project, we will use the Python programming language, and use the TCP/IP protocols as a communications medium.

To implement this in the course of the semester, we plan to have implemented the stream cipher on the audio stream, the multi-party key exchange, and the authentication mechanism individually by the end of the month of February, and the audio transmission and encryption by the end of the month of March.
