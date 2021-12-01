"""file upload wrapper"""
import ipywidgets as widgets 

class FileUpload(widgets.FileUpload):
    """file upload wrapper"""
    def __init__(self, value: None = None, **kwargs):
        super().__init__(**kwargs)