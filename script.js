const END_OF_RESPONSE_MARKER = "__RESPONSE_COMPLETE__";

// 获取聊天窗口元素
const chatWindow = document.querySelector('.dialog-window');  
// 获取用户输入框元素
const userInput = document.querySelector('.dialog-input');  
// 创建WebSocket连接至服务器
const ws = new WebSocket('ws://localhost:8000/ws/chat'); 
// 获取发送按钮元素
const sendButton = document.querySelector('.dialog-send-btn'); // 获取发送按钮元素 

// 当WebSocket连接建立时，输出日志到控制台
ws.onopen = function(event) {  
    console.log("Connected to WebSocket server");  
};  

// 当接收到WebSocket消息时，将消息内容添加到聊天窗口，并滚动到底部
ws.onmessage = function(event) {  
    const message = event.data;  
    const p = document.createElement('span');  
    p.textContent = message;  
    chatWindow.appendChild(p);  
    chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to bottom
};  

// 更新发送按钮状态的函数
function updateSendButtonState() {
    sendButton.disabled = !userInput.value.trim();
}

// 初始化时更新一次按钮状态
updateSendButtonState();

// 监听用户输入以实时更新按钮状态
userInput.addEventListener('input', updateSendButtonState);

// sendMessage函数用于处理发送消息逻辑
function sendMessage() {
    if (!sendButton.disabled) { // 只有在按钮未禁用时才发送消息
        const message = userInput.value;

        // 在发送消息前禁用输入框和发送按钮
        userInput.disabled = true;
        sendButton.disabled = true;

        ws.send(message);
        // 在聊天窗口添加一条用户消息，并带有'User: '前缀
        const p = document.createElement('p');
        p.textContent = 'User: ' + message;
        chatWindow.appendChild(p);
        // 滚动聊天窗口到底部，显示最新消息
        chatWindow.scrollTop = chatWindow.scrollHeight; 
        // 清空输入框
        userInput.value = ''; 
        // 更新按钮状态
        userInput.disabled = false;
        updateSendButtonState();
    }
}

// 添加键盘监听事件，当按下Enter键时触发sendMessage函数
userInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') { // 检查是否按下了回车键
        if (event.ctrlKey || event.metaKey) { // 检查是否同时按下了Ctrl键（Windows/Linux）或Command键（Mac）
            // 实现换行功能
            let start = this.selectionStart;
            let end = this.selectionEnd;
            this.value = this.value.slice(0, start) + '\n' + this.value.slice(end);
            this.setSelectionRange(start + 1, start + 1);
        } else{
            event.preventDefault(); // 阻止默认的表单提交行为（如果input是form的一部分）
            sendMessage();    
        }
        
    }

});