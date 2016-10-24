

How to run the file
./srget -o output file -c http://someurl.domain[:port]/path/to/file
./srget -o output file -c numConn http://someurl.domain[:port]/path/to/file


Whats Missing
	- Resume 
	- Redirect

How my program works.

1) The Main function handles some of the initai variables and determines if the command entered into the console is valid. Also take note that there is a variable called thread_status_list that will become very importatant as this will be used later to check if chuck download is True or False. 


2) Since I was not able to handle resume. We then enter the download_preparation function. What this function does is it takes the content length, range and number of connections and gives us the starting points, ending points. With this we are then able to zip our two lists together. We also create a thread here that will call the function thread_handler


3) once in thread handler the we split our content_range into smaller chuncks so what we get is a certain number of chunks will be pre-devided in the download_preparation function and then the thread_handler function will break them down into smaller sizes to download. 


4) This then sends it to the downloader to download the file. 


