python-IR-demodulation
======================

Python programme to demodulate signals from an infrared receiver.

Samuel Colvin June 2013.

The program can be used to trigger actions such as play or pause music, click a button or potentially anything based on input from any IR transmitter eg. TV or audio remote control.

Works with an infrared reciever like [this](http://www.networkedmediatank.com/showthread.php?tid=29013) plugged into the mic port.

I've tested and used it with a Cambridge Audio remote Model: RC-340AC. Small changes to settings.py should allow it to be used with another remote.

Requirements: pyaudio, matplotlib, scipy, numpy, pickle and some other pretty standard python modules.

Currently running on Windows 7 and not tested on any other platforms.


Usage:

<!--usage-->

	python-IR-demodulation, usage:
	
	python irdemod.py setup_refs || learn_actions || plot_signal || verbose_test || run_active
	
	setup_refs: generates an expected profile for the beginning of messages recieved IR reciever. 
		This profile is then used when running to detect whether a message has been recieved.
	
	learn_actions: learns button binary codes based on your choices and inputs from reciever.
	
	plot_signal: plot signal a recieved IR message and information about processing.
	
	verbose_test: verbose test of the demodulation without actually calling any of the button presses.
	
	run_active: actually run the program and press buttons based on IR signals. 
	
<!--/usage-->

