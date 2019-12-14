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
