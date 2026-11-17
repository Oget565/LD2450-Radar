---
title: "LD2450 + Lidar Radar"
github: "https://github.com/Oget565/LD2450-Radar"
description: "A radar device that utilizes a combination of LD2450 millimeter wave radars and a lidar to create a radar capable of detecting living things in the radius of about 6 meters. It consists of 2 modules: a standalone radar and a separate screen that displays live feed from the sensors. Can be used as a defense system."
created_at: "2026-11-04"
total_time: "21h 42m"
---

# November 5, 2026: Started doing a schematic
<!-- fabricate:entry 2213 -->

I started my project by creating a schematic of all of the electronic components first. I did some research and landed on the ESP32-S3-WROOM1 as the best fit for my project, since it has enough UART ports for all of the sensors

![](https://fabricate.hackclub-assets.com/616735339f1caf3ef49052b8f50ca4e0371438838814ebb143497baf9625ee32/image-png/image.png)

First, I added the core components first, like the ESP32 and LD2450 sensors. Alongside doing that, I also filled my AliExpress cart with those components, so I can know the estimated cost

![](https://fabricate.hackclub-assets.com/f26fa3df4c972ae02f1c3dccfd7de267eac787261c8352f6f9d126034b90abab/image-png/image.png)

Next, I started working on wiring the components to each other. This is pretty easy because the ESP32 already comes with all of the regulators and extra components inside. All I need to do is add an IC that would provide a stable 3.3v and connect a USB-C port to the microcontroller. Connecting sensors is straightforward because they communicate using UART UX and RX pins.

![](https://fabricate.hackclub-assets.com/2a37468908dc049dab0b0d25d2a363608d89a91e0a8bc1bda1ec1bf6db689688/image-png/image.png)

Finally, I made my schematic neat and easy to read. I still need to finish wiring the sensors and create a second schematic for a separate screen, but it should be easy.

**Total time spent: 2h 30m**

# November 5, 2026 (entry 2): Finished the radar module schematic
<!-- fabricate:entry 2223 -->

Finished the schematic for the radar module itself. Found out that it needs 5V, so I had to add a boost module. I also created a second schematic for the separate display module, but haven't started on it yet.

![](https://fabricate.hackclub-assets.com/597d90456980ae4325b9540f2907835f3db3de2a369f504ef0cf2886edd9ab11/image-png/image.png)

**Total time spent: 1h 12m**

# November 6, 2026: Made the PCB
<!-- fabricate:entry 2286 -->

I started making the PCB. First of all, I created the border, and it will be 60 by 60 mm.
![](https://fabricate.hackclub-assets.com/b4c1231131c0694b32f384fcfc38aa2713c66d38361b24ab42a28f0c079d8d29/image-png/image.png)

Then, I placed all of the components at their places before actually doing any wiring. I didn't take a lot of time and was pretty primitive.
![](https://fabricate.hackclub-assets.com/da5931d68a49736254799068efc8b94e6bdf8b9a2b333811d57d4ccfa74d31c1/image-png/image.png)

After all of the components were placed, I wired them together. This was the most time-consuming part, but I managed to do it. Here is the finished PCB:

![](https://fabricate.hackclub-assets.com/9ec3616c8fbe59bfffb0b56164ddcf0fa0b5ff0b3be238883ae7fc1b22c99a6e/image-png/image.png)
![](https://fabricate.hackclub-assets.com/c40056dc6e9f239f22bd11dad153fc7e677c0250724a8d716faca9bce11694c5/image-png/image.png)

**Total time spent: 3h**

# November 7, 2026: Started doing the case
<!-- fabricate:entry 2372 -->

I finished doing my schematic for the screen, which was super simple since its just esp32 and a diaplay. Then, I started doing the actual case for the radar in CAD, and I did the main body. I will be working on finishing the lid with all of the sensors next.
![](https://fabricate.hackclub-assets.com/39b90aad37d263a60d07a90dd54b3c884739b485ed3a5b55ed385547cea79dce/image-png/image.png)

**Total time spent: 3h 30m**

# November 8, 2026: Finished the case
<!-- fabricate:entry 2409 -->

I already had the case done, so I had to finish the lid with all of the sensors. I started by creating a sketch with 2 LD2450 modules.
![](https://fabricate.hackclub-assets.com/8bb3f4443b5511db58528a5c8323eaaac0b8aea442dee8b288ac8e5c57122095/image-png/image.png)
After I made the sketch, I mirrored them at 76 degrees of internal angle which will produce ~224 degrees of combines field of view. 
![](https://fabricate.hackclub-assets.com/21f4e7f0dbdd25bfabd0183ddab845cc36ad6ea7c1143434601056dd6a1124d8/image-png/image.png)
This is the finished model which is ready to be 3d printed.
![](https://fabricate.hackclub-assets.com/5479d33fb6d5d71a2be2bdacf370d5cfe3fa5814e2ae6fb33c26f142c7854adc/image-png/image.png)

**Total time spent: 2h 30m**

# November 8, 2026 (entry 2): Worked on GitHub Repo
<!-- fabricate:entry 2415 -->

I worked on creating the GitHub repo; I made a README file, completed the BOM, and uploaded all of the necessary files. I will work on the firmware next.
![](https://fabricate.hackclub-assets.com/1f1a672dada6de5d24d5c47128402d8640176d90a2f75f5a861645f455faf6d9/image-png/image.png)

**Total time spent: 1h**

# November 8, 2026 (entry 3): Finished the code
<!-- fabricate:entry 2472 -->

I started working on the code for the ESP32. Since there are 2 parts, I had to write 2 different pieces of code. At first, I connected two ESP32s using the ESPNOW library, and I was surprised by how fast it was.
![](https://fabricate.hackclub-assets.com/68198be8011501c43a3be0518550962e9136af69f7348e9fa9bbef4b4a5ab87c/image-png/image.png)
Then I started working on the actual code for the radar and lidar. It is difficult since I don't have access to the module itself. I had to search the internet, and by doing so, I found some chunks of code that can be used as a library for the modules.
![](https://fabricate.hackclub-assets.com/3866cbf32a044d937e38e55c2b32b519506edb10119da4c7d8c2209b8e7e83a4/image-png/image.png)
I also wrote the code for the display, but I am not sure how it would look since I don't have access to the display yet.

**Total time spent: 2h 30m**

# November 11, 2026: Fixed mistakes before resubmitting
<!-- fabricate:entry 2634 -->

![](https://fabricate.hackclub-assets.com/101ec5a8d9fbfc304ab45a4e1bfb60ccdd0fdd84cc275892d0ec22093cdb10aa/image-png/image.png)
![](https://fabricate.hackclub-assets.com/f54fcd162ae668f58bad13f0f61378e2ea8d23eb4666a52af06c6acbda9a884a/image-png/image.png)
I worked on my project after I got the feedback, and fixed several mistakes. I completely rerouted the PCB, making everything look more pleasing and fixed some electrical issues as well. I also added the modules to my CAD models, so it is easier to understand what goes where

**Total time spent: 2h**

# November 17, 2026: Worked on polishing the project
<!-- fabricate:entry 3358 -->

![](https://fabricate.hackclub-assets.com/06e29459482b22b0f8a1d0eb0e079cbffa67777b5ec67652a547bee3f741ef21/image-png/image.png)
![](https://fabricate.hackclub-assets.com/adf0a0b2af1236d5e7ed09ef93f4a7a7784f74cd9ec0f3c5805fca868c722dd0/image-png/image.png)
I worked on my project after it got rejected. I polished the pcb, fixed some of the electical errors, made the CAD files look more polished, like a real product, and rendered them. I hope this time my project will get accepted

**Total time spent: 3h 30m**
