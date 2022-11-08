from PIL import Image
if __name__=="__main__":
    #Read the two images
    image1 = Image.open('C:\\Users\\benja\\Desktop\\insert_test.png').convert('RGBA')
    image2 = Image.open('C:\\Users\\benja\\Desktop\\test1.png').convert('RGBA')
    image3 = Image.open('C:\\Users\\benja\\Desktop\\test2.png').convert('RGBA')
    #resize, first image
    image1_size = image1.size
    image2_size = image2.size
    new_image = Image.new('RGBA', (image1_size[0], image1_size[1]), (250, 250, 250))
    new_image.paste(image1, (0, 0), image1)
    new_image.paste(image2, (50, 50), image2)
    new_image.paste(image3, (50, 75), image3)
    new_image.save('C:\\Users\\benja\\Desktop\\merged.png', "PNG")
    new_image.show()