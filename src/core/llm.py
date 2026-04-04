import lmstudio as lms

model = lms.llm("qwen2.5-0.5b-instruct")

response = model.respond("/no_think What is the capital of France?", )
print(response.content)