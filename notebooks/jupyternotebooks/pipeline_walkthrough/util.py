from IPython.display import Image

def show_image(path, height=1600, width=1200):
    return Image(filename=path,height=height, width=width) 
