from abc import ABC, abstractmethod
from PIL import Image, ImageOps
import numpy as np
from io import BytesIO
import base64
import re


class Component(ABC):
    def __init__(self, name, inports=None, outports=None):
        self.name = name
        self.description = ""
        self.inports = inports
        self.inputs_types = {}
        self.outports = outports

    @abstractmethod
    def execute(self):
        pass

    def __str__(self):
        return self.name


class LoadImage(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.inports = inports
        self.inputs_types = {"Image": "Image"}
        self.description = "This component loads an image from the given path."
        self.outports = {"Image": Image.open}
        self.img = None  # returns a numpy array which is the image
        self.path = None
        self.image_data = None

    def __str__(self):
        return super().__str__()

    def set_parameters(self, args):
        '''Sets the path of the image, call this function when user changes the path in the web editor '''
        self.image_data = re.sub('^data:image/.+;base64,', '', args['file'])

    def execute(self):
        # inp = input("Enter the path of the image: ")
        self.img = Image.open(BytesIO(base64.b64decode(self.image_data)))
        self.outports["Image"] = self.img
        return self.img


class GetInteger(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.inputs_types = {"Integer": "Integer"}
        self.description = "This component gets an integer from the user."
        self.args = None

    def __str__(self):
        return super().__str__()

    def set_parameters(self,args):
        self.args = args

    def execute(self):
        inp = self.args[0]
        self.outports = {"Integer": int(inp)}
        return int(inp)


class GetFloat(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.inputs_types = {"Float": "Float"}
        self.description = "This component gets a float from the user."
        self.args = None

    def __str__(self):
        return super().__str__()

    def set_parameters(self,args):
        self.args = args

    def execute(self):
        inp = self.args[0]
        self.outports = {"Float": float(inp)}
        return float(inp)


class Crop(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.inputs_types = {"X Coordinate": "Integer", "Y Coordinate": "Integer", "Width": "Integer", "Height": "Integer"}
        self.description = "This component crops the image."

        self.x = 0  # x coordinate of the top left corner
        self.y = 0  # y coordinate of the top left corner
        self.w = 0  # width of the cropped image
        self.h = 0  # height of the cropped image
        # TODO: add here to getinteger and getfloat

    def __str__(self):
        return super().__str__()

    def set_parameters(self, args):
        '''Sets the crop area of the image, call this function when user changes the crop area values in the web editor '''
        self.x = int(args['x'])
        self.y = int(args['y'])
        self.w = int(args['width'])
        self.h = int(args['height'])

    def execute(self):
        img = self.inports["Image"]  # the image to be cropped
        cropped_img = img.crop((self.x, self.y, self.x + self.w, self.y + self.h))  # returns the cropped image
        self.outports = {"Image": cropped_img}
        return cropped_img


class GetDimensions(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.inputs_types = {"Image": "Image"}
        self.description = "This component gets the dimensions of the image."

    def __str__(self):
        return super().__str__()

    def execute(self):
        img = self.inports["Image"]  # the image to get the dimensions of
        self.outports = {"Height": int(img.shape[0]), "Width": int(img.shape[1])}
        return int(img.shape[0]), int(img.shape[1])  # returns the height and width of the image


class Rotate(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.inputs_types = {"Angle": "Integer"}
        self.description = "This component rotates the image."
        self.angle = 0 # angle to rotate the image

    def __str__(self):
        return super().__str__()

    def set_parameters(self, args):
        self.angle = int(args['angle'])

    def execute(self):
        img = self.inports["Image"]  # the image to be rotated
        rotated_img = img.rotate(self.angle, expand=True)  # returns the rotated image
        self.outports = {"Image": rotated_img}
        return rotated_img


class Stack(Component):
    def __init__(self, name="Stack", inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.description = "This component stacks two images on top of each other."
        self.inputs_types = {"Image1": "Image", "Image2": "Image"}
        self.inports = {}

    def __str__(self):
        return super().__str__()

    def execute(self):
        img1 = self.inports["Image"]
        img2 = self.inports["Image2"]       # TODO: edit here when assignment in the graph.execute function, x.inports = y.outports
        width1, height1 = img1.size
        width2, height2 = img2.size
        new_img = Image.new('RGB', (max(width1, width2), height1 + height2))
        new_img.paste(img1, (0, 0))
        new_img.paste(img2, (0, height1))
        self.outports = {"Image": new_img}
        return new_img  # ISSUE:


class HStack(Component):
    def __init__(self, name="HStack", inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.description = "This component stacks two images side by side."
        self.inputs_types = {"Image1": "Image", "Image2": "Image"}
        self.inports = {}

    def __str__(self):
        return super().__str__()

    def execute(self):
        img1 = self.inports["Image"]
        img2 = self.inports["Image2"]       # TODO: edit here when assignment in the graph.execute function, x.inports = y.outports
        width1, height1 = img1.size
        width2, height2 = img2.size
        new_img = Image.new('RGB', (width1 + width2, max(height1, height2)))
        new_img.paste(img1, (0, 0))
        new_img.paste(img2, (width1, 0))
        self.outports = {"Image": new_img}
        return new_img  # ISSUE:


class Scale(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.description = "This component scales the image."
        self.inputs_types = {"Scale Factor": "Float"}
        self.scale = 1

    def __str__(self):
        return super().__str__()

    def set_parameters(self, args):
        self.scale = int(args['x'])

    def execute(self):
        img = self.inports["Image"]
        new_size = (int(img.size[0] * self.scale), int(img.size[1] * self.scale))
        scaled_img = img.resize(new_size)
        self.outports = {"Image": scaled_img}
        return scaled_img


class Fit(Component):
    def s__init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.description = "This component fits the image to the given dimensions."
        self.inputs_types = {"Width": "Integer", "Height": "Integer"}

        self.width = 0
        self.height = 0

    def __str__(self):
        return super().__str__()

    def set_parameters(self, args):
        self.width = int(args['width'])
        self.height = int(args['height'])

    def execute(self):
        img = self.inports["Image"]
        fitted_img = img.resize((self.width, self.height), resample=Image.BILINEAR)
        self.outports = {"Image": fitted_img}
        return fitted_img


class Stretch(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.description = "This component stretches the image to the given dimensions."
        self.inputs_types = {"Width": "Integer", "Height": "Integer"}
        self.current_width,self.current_height= 0,0

        self.width = 0 # width to stretch the image
        self.height = 0 # height to stretch the image

    def __str__(self):
        return super().__str__()

    def set_parameters(self,args):
        self.width = int(args['width factor'])
        self.height = int(args['height factor'])

    def execute(self):
        img = self.inports["Image"]
        h = img.size[0] * self.width
        w = img.size[1] * self.height
        stretched_img = img.resize((w, h), resample=Image.BILINEAR)
        self.outports = {"Image": stretched_img}
        return stretched_img


class SaveImage(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)

        self.path = ""
        self.description = "This component saves the image to the given path."
        self.inputs_types = {"Image": "Image"}

        self.inports = {"Image": Image.register_save, "Path": str}
        self.outports = {}

    def __str__(self):
        return super().__str__()

    def set_parameters(self):
        pass

    def execute(self):
        img = self.inports["Image"]
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        # img.close()
        return img_str, 'save'

class ViewImage(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.description = "This component displays the image."
        self.inputs_types = {"Image": "Image"}

    def __str__(self):
        return super().__str__()

    def execute(self):
        img = self.inports["Image"]
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        # img.close()
        return img_str, 'view'

class DupImage(Component):
    def __init__(self, name, inports=None, outports=None):
        super().__init__(name, inports, outports)
        self.description = "This component duplicates the image."
        self.inputs_types = {"Image": "Image"}
        self.img_copy = None
        self.node_path = 0

    def __str__(self):
        return super().__str__()

    def set_parameters(self,args):
        self.node_path = args['node_path']
        img = self.inports["Image"]
        self.img_copy = img.copy()


    def execute(self):
        img = self.inports["Image"]
        self.outports = {"Image": img}
        return img

# #
# if __name__ == '__main__':
#     load = LoadImage("Load Image", [], ["image"])
#     load.execute()
    #
    # crop = Crop("Crop", ["image", "x", "y", "w", "h"], ["image"])
    # crop.inports = load.outports
    # crop.execute()
    #
    # rotate = Rotate("Rotate", ["image"], ["image"])
    # rotate.inports = load.outports
    # rotate.execute()
    #
    # load2 = LoadImage("Load Image", [], ["image"])
    # load2.execute()
    #
    # load2.inports = load.outports
    # #
    # stack = Stack("Stack", {}, ["image"])
    # stack.inports["Image"] = load.outports["Image"]
    # stack.inports["Image2"] = load2.outports["Image"]
    # stack.execute()
    #
    # hstack = HStack("HStack", {}, ["image"])
    # hstack.inports["Image"] = load.outports["Image"]
    # hstack.inports["Image2"] = load2.outports["Image"]
    # hstack.execute()

    # scale = Scale("Scale", ["image"], ["image"])
    # scale.inports = load.outports
    # scale.execute()

    # fit = Fit("Fit", ["image"], ["image"])
    # fit.inports = load.outports
    # fit.execute()
    #
    # stretch = Stretch("Stretch", ["image"], ["image"])
    # stretch.inports = load.outports
    # stretch.execute()

    # dup = DupImage("Dup Image", ["image"], ["image", "image2"])
    # dup.inports = load.outports
    # dup.execute()
    # #
    # save = SaveImage("Save Image", ["image", "path"], [])
    # save.inports = stack.outports
    # save.execute()
    #
    # view = ViewImage("View Image", ["image"], [])
    # view.inports = save.outports
    # view.execute()


