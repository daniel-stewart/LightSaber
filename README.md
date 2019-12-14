# LightSaber
This repo contains files related to creating 3D lightsabers in Blender that can then be printed out and electroincs inserted. 

## Light Saber Maker Python File
This file will create the basic parts for a lightsaber.
1) Open Blender 2.8 or above.
2) Go to the __Scripting__ tab
3) Choose the open button in the editor and load the LightSaberMaker.py file.
4) Hit __Run Scripts__ button.

The basic parts should be created for you. They are very large compared to Blender units because, by default, Blender exports with 1m = 1mm when exporting STL files. Yes, I could change the default, but I tried to make it easy on my students by allowing them to simply export with default settings.

At the bottom of the Python file you'll see the calls to the various functions which create the hilt, pommel, and blade holder. You can alter the parameters that are used to create the parts. You should be able to look at the function definitions to see what each parameter does. The basic parameters control the number of vertices around, the number of threads, the radius of the lightsaber, and the thread profile.

This just creates parts from which you can continue to make into what you want. They should screw together just fine once printed, assuming you've made the number of threads for male and female such that they fit. 

The Blade Holder was sized to fit standard blades you can get within this hobby space. For example, I bought a blade tube from https://www.thecustomsabershop.com/1-Thick-walled-Trans-White-PolyC-40-long-P528.aspx and it fits just fine. 

## M4 Lightsaber Code
The M4 Lightsaber Python file is the code that can be loaded onto an Adafruit M4 Express Feather (https://www.adafruit.com/product/3857) + PropWing (https://www.adafruit.com/product/3988) to turn the lightsaber on and off. It is very basic code that turns the lightsaber on with one press of the external button and turns it back off when the button is pressed again. The sounds are standard 22kHz, 16-bit WAV files. A very basic usage of the "tap" detection is used to play a sound when lightsabers are hit and momentarily turn the blade all white. I have not included the WAV files, as they are not mine to include. Search the web for whatever sound files you like. 

I used a standard battery common for lightsabers - https://www.thecustomsabershop.com/JST-Sony-Li-Ion-18650-37V-15A-3120mAh-PCB-Protected-Rechargeable-Battery-P1451.aspx.

I bought regular 22mm speakers off the Internet to use for my sound. 
