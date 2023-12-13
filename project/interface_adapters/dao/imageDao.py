import concurrent
from concurrent.futures import ThreadPoolExecutor
from project.entities.image import Image
from env import BUCKET_NAME, REGION
from project.frameworks_and_drivers.aws_clients import S3Client

class ImageDao():
    @staticmethod
    def delete_image(key):
        try:
            S3Client.get_instance().client.delete_object(
                Bucket=BUCKET_NAME,
                Key=key
            )
        except ValueError as e:
            raise e

    @staticmethod
    def upload_img(image:Image) -> str:
        try:
            S3Client.get_instance().s3.Bucket(BUCKET_NAME).upload_fileobj(image.image, image.image_name)
            return f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{image.image_name}"
        except ValueError as e:
            raise e

    @staticmethod
    def delete_images(images_key:str) -> None:
        all_objects = S3Client.get_instance().client.list_objects(Bucket=BUCKET_NAME)

        for object in all_objects["Contents"]:
            if images_key in object["Key"]:
                ImageDao.delete_image(object['Key'])

    @staticmethod
    def upload_images(img_list:list[Image]) -> list[str]:
        """upload multiple files into the s3, and return a list with the urls"""
        list_of_urls = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(ImageDao.upload_img, img): img for img in img_list}
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    url = future.result()
                    list_of_urls.append(url)
                except ValueError as e:
                    raise e

        return list_of_urls
