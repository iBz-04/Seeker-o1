from seeker_o1.models.base.base_model import BaseModel
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
import pytesseract

class VisionModel(BaseModel):
    def __init__(self, model_name="BLIP", **kwargs):
        super().__init__(model_name, **kwargs)
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    def generate(self, prompt, system_message=None, temperature=None, max_tokens=None, **kwargs):
        return "VisionModel does not support text generation."
    def generate_with_tools(self, prompt, tools, system_message=None, temperature=None, max_tokens=None, **kwargs):
        return {"error": "VisionModel does not support tool generation."}
    def extract_json(self, prompt, schema, system_message=None, temperature=None, max_tokens=None, **kwargs):
        return {"error": "VisionModel does not support JSON extraction."}
    def get_embedding(self, text, **kwargs):
        return []
    def analyze_image(self, image_path):
        image = Image.open(image_path)
        return {"size": image.size, "mode": image.mode}
    def describe_image(self, image_path):
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(image, return_tensors="pt")
        with torch.no_grad():
            out = self.model.generate(**inputs)
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        return caption
    def read_text(self, image_path):
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip() 