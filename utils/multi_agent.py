import os
import requests
import json

AGENT_MAP = {
    "finny": {"app_id": os.getenv("DIFY_FINNY_APP_ID"), "api_key": os.getenv("DIFY_FINNY_API_KEY")},
    "accy":  {"app_id": os.getenv("DIFY_ACCY_APP_ID"),  "api_key": os.getenv("DIFY_ACCY_API_KEY")},
    "bizzy": {"app_id": os.getenv("DIFY_BIZZY_APP_ID"), "api_key": os.getenv("DIFY_BIZZY_API_KEY")},
    "leader":{"app_id": os.getenv("DIFY_LEADER_APP_ID"),"api_key": os.getenv("DIFY_LEADER_API_KEY")}
}

def run_agent_streaming(prompt, agent_key="finny"):
    config = AGENT_MAP.get(agent_key)
    if not config:
        yield "❌ ไม่มี Agent นี้"
        return
    
    url = "https://api.dify.ai/v1/chat-messages"
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    data = {
        "app_id": config['app_id'],
        "query": prompt,
        "response_mode": "streaming",
        "user": "streamlit-user",
        "inputs": {}
    }
    try:
        with requests.post(url, headers=headers, json=data, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').replace("data: ", "")
                    try:
                        json_data = json.loads(decoded_line)
                        if "answer" in json_data:
                            yield json_data["answer"]
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.RequestException as e:
        yield f"❌ เกิดข้อผิดพลาดจาก Dify Streaming: {str(e)}"

def leader_route(prompt: str) -> str:
    lower_prompt = prompt.lower()
    if any(keyword in lower_prompt for keyword in ["บัญชี", "journal", "coa", "บัญชีแยกประเภท", "เดบิต", "เครดิต"]):
        return "accy"
    elif any(keyword in lower_prompt for keyword in ["วิเคราะห์", "กำไร", "ขาดทุน", "งบการเงิน", "กระแสเงินสด", "รายได้", "งบดุล"]):
        return "finny"
    elif any(keyword in lower_prompt for keyword in ["ธุรกิจ", "swot", "แผน", "กลยุทธ์", "business model"]):
        return "bizzy"
    else:
        return "finny"  # Default fallback
