# pip install diffusers transformers torch ftfy regex


from diffusers import StableDiffusionPipeline
import torch

# 加载模型
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

# 定义提示词
prompt = "A beautiful flower in a vase"
# 生成图像
image = pipe(prompt).images[0]
# 保存图像
image.save("generated_image.png")    