import re, os, time
import urllib

from selenium import webdriver

from pattern.web import URL, DOM


class GoogleImageExtractor(object):
    def __init__(self, search_key=''):
        """ Google image search class
            Args:
                search_key to be entered.

        """
        if type(search_key) == str:
            ## convert to list even for one search keyword to standalize the pulling.
            self.g_search_key_list = [search_key]
        elif type(search_key) == list:
            self.g_search_key_list = search_key
        else:
            print 'google_search_keyword not of type str or list'
            raise

        self.g_search_key = ''

        ## user options
        self.image_dl_per_search = 200

        ## url construct string text
        self.prefix_of_search_url = "https://www.google.com.sg/search?q="
        self.postfix_of_search_url = '&source=lnms&tbm=isch&sa=X&ei=0eZEVbj3IJG5uATalICQAQ&ved=0CAcQ_AUoAQ&biw=939&bih=591'  # non changable text
        self.target_url_str = ''

        ## storage
        self.pic_url_list = []
        self.pic_info_list = []

        ## file and folder  ABSOLUTE path
        self.folder_main_dir_prefix = r'/Users/yourUser/yourPathTo/Download/ImageSetDir/'

    def reformat_search_for_spaces(self):
        """
            Method call immediately at the initialization stages
            get rid of the spaces and replace by the "+"
            Use in search term. Eg: "Cookie fast" to "Cookie+fast"

            steps:
            strip any lagging spaces if present
            replace the self.g_search_key
        """
        self.g_search_key = self.g_search_key.rstrip().replace(' ', '+')

    def set_num_image_to_dl(self, num_image):
        """ Set the number of image to download. Set to self.image_dl_per_search.
            Args:
                num_image (int): num of image to download.
        """
        self.image_dl_per_search = num_image

    def get_searchlist_fr_file(self, filename):
        """Get search list from filename. Ability to add in a lot of phrases.
            Will replace the self.g_search_key_list
            Args:
                filename (str): full file path
        """
        with open(filename, 'r') as f:
            self.g_search_key_list = f.readlines()

    def formed_search_url(self):
        ''' Form the url either one selected key phrases or multiple search items.
            Get the url from the self.g_search_key_list
            Set to self.sp_search_url_list
        '''
        self.reformat_search_for_spaces()
        self.target_url_str = self.prefix_of_search_url + self.g_search_key + \
                              self.postfix_of_search_url

    def retrieve_source_fr_html(self):
        """ Make use of selenium. Retrieve from html table using pandas table.

        """
        driver = webdriver.Firefox()
        driver.get(self.target_url_str)

        ## wait for log in then get the page source.
        try:

            driver.execute_script("window.scrollTo(0, 30000)")
            time.sleep(2)
            source = driver.page_source

            self.temp_page_source = driver.page_source

            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 60000)")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 60000)")
            # for fewer pics remove lines or not :)
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 60000)")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 60000)")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 60000)")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 60000)")

        except:
            print 'not able to find'
            driver.quit()

        self.page_source = driver.page_source

        driver.close()

    def extract_pic_url(self):
        """ extract all the raw pic url in list

        """
        dom = DOM(self.page_source)
        tag_list = dom('a.rg_l')

        for tag in tag_list[:self.image_dl_per_search]:
            if len(tag.attributes) == 4:
                tar_str = re.search('imgurl=(.*)&imgrefurl', tag.attributes['href'])
            else:
                pass

            try:
                self.pic_url_list.append(tar_str.group(1))
            except:
                print 'error parsing', tag

    def multi_search_download(self):
        """ Mutli search download"""
        for indiv_search in self.g_search_key_list:
            self.pic_url_list = []
            self.pic_info_list = []
            self.g_search_key = indiv_search

            self.formed_search_url()
            self.retrieve_source_fr_html()
            self.extract_pic_url()
            self.downloading_all_photos()  # some download might not be jpg?? use selnium to download??
            self.save_infolist_to_file()

    def is_image_watermarked(self, url_link):
        """ check if url_link belongs to a site wich
            use watermarks to protect their pics. These images are
            not suitable for machine learning. Maybe replace
            these funktion with a smart watermark recognition (AI).

        """

        watermarked_imgsites = ["dreamstime", "123rf.com", "first-nature", "hlasek", "stock", "arkive.org",
                                "alamy", "pinimg.com", "freeimages.com"]

        if any(x in url_link for x in watermarked_imgsites):
            return True
        else:
            return False

    def downloading_all_photos(self):
        """ download all photos to particular folder

        """
        self.create_folder()
        pic_counter = 1
        for url_link in self.pic_url_list:
            print pic_counter
            pic_prefix_str = self.g_search_key + str(pic_counter)
            self.download_single_image(url_link.encode(), pic_prefix_str)
            pic_counter = pic_counter + 1

    def download_single_image(self, url_link, pic_prefix_str):
        """ Download data according to the url link given.
            Args:
                url_link (str): url str.
                pic_prefix_str (str): pic_prefix_str for unique label the pic
        """
        self.download_fault = 0
        file_ext = os.path.splitext(url_link)[1]  # use for checking valid pic ext
        temp_filename = pic_prefix_str + file_ext
        temp_filename_full_path = os.path.join(self.gs_raw_dirpath, temp_filename)

        valid_image_ext_list = ['.png', '.PNG', '.jpg', '.jpeg', '.JPG', '.JPEG', '.gif', '.GIF', '.bmp', '.BMP',
                                '.tiff', '.TIFF']  # not comprehensive

        if type(url_link) is int:
            return

        url_link = urllib.unquote(url_link).decode('utf8')
        print (url_link)

        if self.is_image_watermarked(url_link):
            return

        url = URL(url_link)

        try:

            if url.redirect:
                return  # if there is re-direct, return

            if file_ext not in valid_image_ext_list:
                return  # return if not valid image extension

            self.pic_info_list.append(pic_prefix_str + ': ' + url_link)
            downloaded_img = url.download()

            if len(downloaded_img) > 0:  # sometimes download is empty
                f = open(temp_filename_full_path, 'wb')  # save as test.gif
                f.write(downloaded_img)  # if have problem skip
                f.close()
        except:
            # if self.__print_download_fault:
            print 'Problem with processing this data: ', url_link
            self.download_fault = 1

    def create_folder(self):
        """
            Create a folder to put the log data segregate by date

        """

        self.gs_raw_dirpath = os.path.join(self.folder_main_dir_prefix,
                            time.strftime("_%d_%b%y",time.localtime()) + "_" + self.g_search_key.replace('+', '_'))
        if not os.path.exists(self.gs_raw_dirpath):
            os.makedirs(self.gs_raw_dirpath)

    def save_infolist_to_file(self):
        """ Save the info list to file.

        """
        temp_filename_full_path = os.path.join(self.gs_raw_dirpath, self.g_search_key + '_info.txt')

        with open(temp_filename_full_path, 'w') as f:
            for n in self.pic_info_list:
                f.write(n)
                f.write('\n')


if __name__ == '__main__':

    choice = 4

    if choice == 4:
        """test the downloading of files"""
        w = GoogleImageExtractor('')  # leave blanks if get the search list from file

        # absolute path here
        # file should contain one query per line
        searchlist_filename = r'/Users/yourUser/yourPathTo/keywords.txt'  # use absolute path here
        w.set_num_image_to_dl(10)
        w.get_searchlist_fr_file(searchlist_filename)  # replace the searclist
        w.multi_search_download()
