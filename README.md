**Google Image Extractor**
This is usefull Python script (tested with **Python2.7**) for extracting Images from Google Search.
It's a fork from [Simply Python's](https://simplypython.wordpress.com/2015/05/18/saving-images-from-google-search-using-selenium-and-python/) script.
These script downloads the result of google using silenium.

You can change the List inside the `is_image_watermarked()` funktion to avoid downloading from sources that watermarks their images.

- Change `folder_main_dir_prefix` to your desired directory.
- Change the path to your query file in `searchlist_filename`
- Change `w.set_num_image_to_dl(10)` for more images

Have fun :)
