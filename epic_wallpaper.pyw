#!/usr/bin/python
'''epic_wallpaper: Automatically update your desktop wallpaper with the latest
images from NASA's DSCOVR:EPIC mission'''

# Python imports
import urllib2
import os
import json
import ctypes
import time

SPI_SETDESKWALLPAPER = 0x0014

class EpicWallpaper(object):
    """Get EPIC pictures from the web and rotate them as your desktop 
    wallpaper."""
    
    IMG_DIRECTORY = "images"
    URL = "http://epic.gsfc.nasa.gov/"
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        """Remove the image directory."""
        self.cleanup_image_dir(delete=True)
        return
    
    def cleanup_image_dir(self, delete=False):
        """Make sure the image directory is empty and ready for use."""
        
        full_path = os.path.join(os.getcwd(), self.IMG_DIRECTORY)
        if os.path.exists(full_path):
            for filename in os.listdir(full_path):
                os.remove(os.path.join(full_path, filename))
            if delete:
                os.rmdir(full_path)
        elif not delete:
            os.mkdir(full_path)
            
        return full_path
    
    def get_latest_images(self):
        """Fetch the latest set of images from EPIC."""
        
        full_path = self.cleanup_image_dir()
        epic_json = urllib2.urlopen(self.URL + "/api/images.php").read()
        epic_objects = json.loads(epic_json)

        self.image_list = []
        for obj in epic_objects:
            img_name = obj["image"] + ".jpg"
            url = self.URL + "/epic-archive/jpg/" + img_name
            local_img_path = os.path.join(full_path, img_name)
            with open(local_img_path, "wb") as img_file:
                data = urllib2.urlopen(url).read()
                img_file.write(data)
                self.image_list.append(local_img_path)

        print "Downloaded {0} images.".format(len(self.image_list))
        return

    def endless_image_list(self):
        """Endless list of all images currently available."""
        while True:
            for img in self.image_list:
                yield img

    def rotate_through_images(self, delay=3600):
        """Change the desktop wallpaper to each image in turn."""
        for img in self.endless_image_list():
            print "Updating to image: {0}".format(img)
            rc = ctypes.windll.user32.SystemParametersInfoA(
                                              SPI_SETDESKWALLPAPER,
                                              0,
                                              ctypes.create_string_buffer(img),
                                              0)
            print "Return code: {0}".format(rc)
            time.sleep(delay)

if __name__ == "__main__":
    with EpicWallpaper() as EW:
        EW.get_latest_images()
        EW.rotate_through_images()
