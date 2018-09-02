# X-Ray Calibre Plugin
Downloads:
----------------------------------------------------------------------------------------------------------------------------------
[3.1.4](https://github.com/szarroug3/X-Ray_Calibre_Plugin/blob/master/Versions/xray_creator_calibre_plugin_3_1_4.zip?raw=true)

[Older Versions](https://github.com/szarroug3/X-Ray_Calibre_Plugin/releases)

Websites:
----------------------------------------------------------------------------------------------------------------------------------
Github Page: https://github.com/szarroug3/X-Ray_Calibre_Plugin

Mobileread Page: http://www.mobileread.com/forums/showthread.php?p=3301947#post3301947

Some background information on X-Ray and other Kindle Files:
----------------------------------------------------------------------------------------------------------------------------------
X-Ray allows you to get information on key characters and terms from Goodreads. You can do this in one of a few ways.

1. You can highlight the word in question and if the x-ray file has information on it, a popup with a brief description will
	show. It will also show you where this character has been mentioned in the past (will show page number and excerpt where
	mention occurred).
2. You can click X-Ray and search for the word either by looking through the list or using the search bar. Clicking on the word
	will show you the same popup from #1.
	
X-Ray also has a notable clips section which show quotes from Goodreads. If there are not enough Goodreads quotes found, the
	plugin will add more random excerpts so there are least 20 notable clips.

Author profiles allow you to see information on the author such as a bio, other books by the other, etc. You can see this by going
to "About the author" on the menu while the book is open.

Start actions show you a description of the book along with other information such as the reading time and the rating (retrieved
from Goodreads). It will also allow you to mark the book as currently-reading on Goodreads but you need to be signed into Goodreads
on the device and you need to have wifi enabled and connected for this to work. There will be a pop-up showing you this information
when you open a new book but you can also see it by going to "About this book" on the menu while the book is open.

End actions show you recommendations for other books based on the current book (retrieved from Goodreads). It will also allow you
to mark the book as read on Goodreads but you need to be signed into Goodreads on the device and you need to have wifi enabled and
connected for this to work. There will be a pop-up showing you this information when you reach the end of the book.

Note: These files work only work on Amazon products such as the Kindle PW. For more information on X-Ray files, see here:
	http://www.amazon.com/gp/help/customer/display.html?nodeId=200729910#GUID-A867D8C3-365D-417F-BBD7-239A35EB4119

----------------------------------------------------------------------------------------------------------------------------------
	1. Book specific preferences
		- Use "," or ", " as a separator for words in aliases list
		- Input JSON must have format shown in "JSON Template" section below
	2. Create/Update files for selected books
	3. Send previously generated files to device
	4. General Preferences

	Note: Creating files using this plugin will use the ASIN already in the book so you don't need to update it.
	Note: Highlighting words should work but I have not tested with a book that has DRM so I don't know if it will work for them.

JSON Template:
----------------------------------------------------------------------------------------------------------------------------------
	{"characters":	{"Character1 Name":	{"description": "Character1 Description",
	                          		     "aliases": ["Character1 Alias1", ...]},
	                 "Character2 Name":	{"description": "Character2 Description",
	                          		     "aliases": ["Character1 Alias2", ...]},
			 ...},
 	"settings": 	{"Setting1 Name":	{"description": "Setting1 Description",
	                           		    "aliases": ["Setting1 Alias1", ...]}
			 ...},
  	"quotes":	["Quote1",
	            	 "Quote2",
			 ...]}

Preferences:
----------------------------------------------------------------------------------------------------------------------------------
	1. Send files to device if connected
		- After creating files, files will automatically be sent to device
	2. Create files that don't already exist when sending to device
		- When sending previously generated files, files will be generated for selected books that haven't already been created
	3. Auto associate split aliases, when enabled, will split aliases retrieved from Goodreads up
		- i.e If a character on goodreads named "Vin" has a Goodreads alias of "Valette Renoux", this option will add
			"Valette" and "Renoux" as aliases. You may not want this in cases such as "Timothy Cratchit" who has a
			Goodreads alias of "Tiny Tim". Having this feature on would add "Tiny", and "Tim" as
			aliases which is not valid.
	4. Overwrite local files that already exist when creating files
		- When using the Create/Update Files function, this will decide whether or not to delete local files that already exist
	5. Overwrite files on device that already exist when sending files
		- When using the Send Files function, this will decide whether or not to delete files on the device that already exist
	6. Files to create/send
		- This will let you choose what type of files to create and/or send
		- You must choose at least one.
	7. Book types to create files for
		- Selection of formats to consider when creating and sending files.
		- You must choose at least one.
	8. If device has both (mobi and azw3) formats, prefer
		- This will choose which format to send files for if your device has both file formats
		- This matters because there are offsets in the x-ray file that determine whether something that is highlighted is
			part of the x-ray
		- If you are sure you only have one format of the book type on the device, this does not matter.

Theming:
----------------------------------------------------------------------------------------------------------------------------------
    You can place a file at "\calibre\resources\images\X-Ray Creator\icon.png" (in your calibre application directory) to
    change the plugin's icon.
    

Testing:
----------------------------------------------------------------------------------------------------------------------------------
	This plugin has been tested using a Kindle PW2 on Windows 10 and Linux.
	We are still actively developing the plugin so if you do find a bug or want to request a feature, please let me know via
		Github or Mobileread.

Donations:
----------------------------------------------------------------------------------------------------------------------------------
[Paypal](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=szarroug3%40gmail%2ecom&lc=US&item_name=X%2dRay%20Calibre%20Plugin&no_note=0&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHostedGuest)
