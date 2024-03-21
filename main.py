from fastapi import FastAPI, WebSocket 
from fastapi.responses import StreamingResponse  
import asyncio  
import random  
import time  

from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

device = "cpu" # the device to load the model onto
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen1.5-0.5B-Chat",
    torch_dtype="auto",
    device_map="auto")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-0.5B-Chat")

# 定义一个特殊标记
SPECIAL_END_MARKER = "__RESPONSE_COMPLETE__"

def get_response(input_sentence):
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": input_sentence}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return (response)
  
app = FastAPI()  

phrases = [  
        "Hello, how are you?",  
        "I'm fine, thank you. And you?",  
        "I'm good, thanks for asking.",  
        "What's new?",  
        "Not much, just the usual.",  
        "Have a nice day!",  
        "You too!",  
    ]  

@app.websocket("/ws/chat")  
async def websocket_endpoint(websocket: WebSocket):  
    await websocket.accept()  
    try:  
        async for message in websocket.iter_text():  
            if message:  
                # 处理用户输入  
                print(f"User: {message}")  

                # 发送 "Bot: " 前缀  
                prefix = "Bot: "  
                for char in prefix:  
                    await asyncio.sleep(0.1)  
                    await websocket.send_text(char)     
                                  
                # 随机选择一句回复  
                response = get_response(message)  
                
                # 模拟打字机效果发送回复  
                for char in response:  
                    await asyncio.sleep(0.1)  # 模拟打字速度  
                    await websocket.send_text(char)  
                  
                # 在发送完句子后发送换行符或空格  
                await websocket.send_text("\n")  

                # 发送一个特殊标记表示回复已发送完毕
                #await websocket.send_text(f"{SPECIAL_END_MARKER}\n")
                  
                # 模拟其他处理时间，比如API调用  
                await asyncio.sleep(random.random())  
                  
    except WebSocketDisconnect:  
        print("WebSocket connection closed")

async def simulate_conversation():  
      
    while True:  
        # 随机选择一句对话  
        phrase = random.choice(phrases)  
        # 模拟处理时间，例如等待用户输入或API调用  
        await asyncio.sleep(random.random())  
        # 发送对话的一部分到客户端  
        yield phrase + "\n"  
        # 可以根据需要添加退出条件，例如特定的用户输入  
        if phrase == "Have a nice day!":  
            break  
  
@app.get("/chat")  
async def chat():  
    return StreamingResponse(simulate_conversation(),media_type="text/event-stream")  
  
if __name__ == "__main__":  
    import uvicorn  
    uvicorn.run(app, host="0.0.0.0", port=8000)