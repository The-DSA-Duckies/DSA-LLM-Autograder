# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM
# import deepspeed

model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)

# model.save_pretrained('../../../blue/kapooramanpreet/benjamincortese/mixtral_model')
# tokenizer.save_pretrained('../../../blue/kapooramanpreet/benjamincortese/mixtral_tokenizer')

device_map = {
    "cuda:0": list(range(0, 13)),
    "cuda:1": list(range(13, 26)),
    "cpu": list(range(26, 39))
}

model = AutoModelForCausalLM.from_pretrained('../../../blue/kapooramanpreet/benjamincortese/mixtral_model', device_map='auto')
tokenizer = AutoTokenizer.from_pretrained('../../../blue/kapooramanpreet/benjamincortese/mixtral_tokenizer', device_map='auto')

# model.encoder.to('cuda:0')
# model.decoder.to('cudo:1')

# model.parallelize(device_map)

text = "What do you eat with Bananas?"
inputs = tokenizer(text, return_tensors="pt")

outputs = model.generate(**inputs, max_new_tokens=120)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))