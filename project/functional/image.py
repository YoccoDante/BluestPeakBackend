from project.interface_adapters.dao.imageDao import ImageDao
from project.entities.image import Image
from flask_pymongo import ObjectId
from project.interface_adapters.dao.imageDao import ImageDao
from PIL import Image as PilImage
import io
import os

class ImageController():
    """this class is used to controll the work flow with images,
    doesn't have a route in the flask app"""
    @staticmethod
    def validate_file_size(file, max_size=20971520):  # 10MB
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        return size <= max_size

    @staticmethod
    def validate_extenstion(file_name:str) -> bool:
            """This method validades the extention of a single file, in order to validate it,
            the file name must be passed.\n
            Extentions aveilable: ["png","jpg","jpeg","jfif"]"""
            ALLOWED_EXTENSIONS = set(["png","jpg","jpeg","jfif"])
            return "." in file_name and file_name.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_extentions(imgs:list) -> bool:
        """Recieves a list of images straight from the request, and checks if the extention is permitted.\n
        Extentions availables: ["png","jpg","jpeg","jfif"]"""        
        for img in imgs:
            if not ImageController.validate_extenstion(img.filename):
                return False
        
        return True
    
    @staticmethod
    def upload_product_images(imgs:list, owner_id:str, new_product_id:str, enterprise_id:str) -> list[str]:
        """Pass the image list straight from the request.
        The function upload the images to the storage
        and returns a list with a url for every image passed.\n
        The url has the sintax:\n
        new_url = owner_id/new_product_id/new_image_id"""
        img_list:list[Image] = []
        for img in imgs:
            if not ImageController.validate_extenstion(img.filename):
                raise ValueError("Invalid file extension")
            if not ImageController.validate_file_size(img):
                raise ValueError("File is too large")

            # Convert the image to WebP
            pil_img = PilImage.open(img)
            webp_img_io = io.BytesIO()
            pil_img.save(webp_img_io, 'WebP', quality=80)

            # Create a new file-like object to hold the WebP image data
            webp_img = io.BytesIO(webp_img_io.getvalue())
            webp_img.name = img.filename.rsplit(".", 1)[0] + '.webp'

            new_img_name = f"{str(ObjectId())}.webp"
            new_image = Image(
                image_name='/'.join([enterprise_id,owner_id,new_product_id,new_img_name]),
                owner_id=owner_id,
                image=webp_img,
            )
            img_list.append(new_image)
        
        try:
            urls =ImageDao.upload_images(img_list)
        except ValueError as e:
            raise e

        return urls

    @staticmethod
    def update_images(old_imgs, new_imgs, owner_id, product_id):
        # Delete old images
        for img_key in old_imgs:
            ImageController.delete_image(img_key)

        # Upload new images and get their URLs
        list_of_urls = ImageController.upload_product_images(
            imgs=new_imgs,
            owner_id=owner_id,
            new_product_id=product_id
        )

        return list_of_urls
    
    @staticmethod
    def delete_images(images_key:str) -> None:
        """This method deletes images from a specific profile or product,
        in order to delete images the key must be the _id of the owner"""
        ImageDao.delete_images(images_key=images_key)
    
    @staticmethod
    def upload_profile_pic(image, owner_id:str, enterprise_id:str) -> str:
        """the method creates the Image object in it,
        so the file must be passed straight from the request and returns a url.\n
        Url sintax:\n
        owner_id/image_id . extention"""

        # Convert the image to WebP
        pil_img = PilImage.open(image)
        webp_img_io = io.BytesIO()
        pil_img.save(webp_img_io, 'WebP', quality=80)

        # Create a new file-like object to hold the WebP image data
        webp_img = io.BytesIO(webp_img_io.getvalue())
        webp_img.name = image.filename.rsplit(".", 1)[0] + '.webp'

        new_image_name = '/'.join([enterprise_id,owner_id,str(ObjectId())]) + ".webp"
        new_image = Image(
            image_name=new_image_name,
            image=webp_img,
            owner_id=owner_id
        )
        try:
            new_pic_url = ImageDao.upload_img(image=new_image)
        except ValueError as e:
            raise e
        return new_pic_url
    
    @staticmethod
    def delete_img(img_key:str) -> None:
        """this method must be used just in case the whole key of a image is known,
        if just a segment of the key needs to be passed, the method ImageController.delete_images(partial_key) must me used."""
        try:
            ImageDao.delete_image(img_key)
        except ValueError as e:
            raise e