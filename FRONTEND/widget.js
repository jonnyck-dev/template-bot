(function(){
var API_BASE=(document.currentScript?document.currentScript.getAttribute("data-api-base")||"http://localhost:8020":"http://localhost:8020");
var BUSINESS_NAME=(document.currentScript?document.currentScript.getAttribute("data-business")||"Asistente":"Asistente");
var style=document.createElement("style");
style.textContent='.tbw-chat-btn,.tbw-chat-panel *{box-sizing:border-box;margin:0;padding:0}'
+'.tbw-chat-btn{position:fixed;bottom:20px;right:20px;width:60px;height:60px;border-radius:50%;background:#00BFFF;color:#fff;border:none;cursor:pointer;z-index:999999;box-shadow:0 4px 16px rgba(0,0,0,.25);display:flex;align-items:center;justify-content:center;transition:transform .2s}'
+'.tbw-chat-btn:hover{transform:scale(1.1)}'
+'.tbw-chat-btn svg{width:28px;height:28px;fill:#fff}'
+'.tbw-chat-panel{position:fixed;bottom:90px;right:20px;width:360px;height:500px;background:#fff;border-radius:16px;box-shadow:0 8px 32px rgba(0,0,0,.2);z-index:999998;display:none;flex-direction:column;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;font-size:14px;line-height:1.5;color:#000}'
+'.tbw-chat-panel.tbw-open{display:flex}'
+'.tbw-header{background:#00BFFF;color:#fff;padding:16px;font-weight:600;display:flex;justify-content:space-between;align-items:center}'
+'.tbw-header span{font-size:15px}'
+'.tbw-close{background:none;border:none;color:#fff;font-size:22px;cursor:pointer;padding:0 4px}'
+'.tbw-messages{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}'
+'.tbw-msg{max-width:85%;padding:10px 14px;border-radius:16px;font-size:13px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word}'
+'.tbw-msg.user{background:#00BFFF;color:#fff;align-self:flex-end;border-bottom-right-radius:4px}'
+'.tbw-msg.bot{background:#e8e8e8;color:#000;align-self:flex-start;border-bottom-left-radius:4px}'
+'.tbw-input-area{display:flex;padding:12px;border-top:1px solid #e0e0e0;gap:8px}'
+'.tbw-input-area input{flex:1;padding:10px 14px;border:2px solid #d0d0d0;border-radius:24px;outline:none;font-size:13px;transition:border-color .2s}'
+'.tbw-input-area input:focus{border-color:#00BFFF}'
+'.tbw-input-area button{padding:10px 18px;background:#00BFFF;color:#fff;border:none;border-radius:24px;font-weight:600;cursor:pointer;font-size:13px;transition:background .2s}'
+'.tbw-input-area button:hover{background:#0099CC}'
+'.tbw-input-area button:disabled{background:#b0b0b0;cursor:not-allowed}'
+'.tbw-typing{display:flex;align-items:center;gap:4px;padding:10px 14px;background:#e8e8e8;border-radius:16px;align-self:flex-start;border-bottom-left-radius:4px}'
+'.tbw-typing span{width:7px;height:7px;border-radius:50%;background:#888;animation:tbw-bounce 1.4s infinite ease-in-out}'
+'.tbw-typing span:nth-child(2){animation-delay:.2s}'
+'.tbw-typing span:nth-child(3){animation-delay:.4s}'
+'@keyframes tbw-bounce{0%,60%,100%{opacity:.3;transform:scale(.8)}30%{opacity:1;transform:scale(1)}}';
document.head.appendChild(style);
var btn=document.createElement("button");btn.className="tbw-chat-btn";btn.id="tbw-btn";btn.setAttribute("aria-label","Abrir chat");
btn.innerHTML='<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>';
document.body.appendChild(btn);
var panel=document.createElement("div");panel.className="tbw-chat-panel";panel.id="tbw-panel";
panel.innerHTML='<div class="tbw-header"><span id="tbw-title">'+BUSINESS_NAME+'</span><button class="tbw-close" id="tbw-close">&times;</button></div><div class="tbw-messages" id="tbw-msgs"><div class="tbw-msg bot">Bienvenido al asistente. Hazme cualquier pregunta sobre el negocio.</div></div><div class="tbw-input-area"><input type="text" id="tbw-input" placeholder="Escribe tu pregunta..." /><button id="tbw-send">Enviar</button></div>';
document.body.appendChild(panel);
var msgs=document.getElementById("tbw-msgs");var input=document.getElementById("tbw-input");var send=document.getElementById("tbw-send");var close=document.getElementById("tbw-close");var isStreaming=false;
function addMsg(content,role){var div=document.createElement("div");div.className="tbw-msg "+role;div.textContent=content;msgs.appendChild(div);msgs.scrollTop=msgs.scrollHeight}
function showTyping(){var div=document.createElement("div");div.className="tbw-typing";div.id="tbw-typing";div.innerHTML="<span></span><span></span><span></span>";msgs.appendChild(div);msgs.scrollTop=msgs.scrollHeight}
function removeTyping(){var el=document.getElementById("tbw-typing");if(el)el.remove()}
function updateBot(content){var last=msgs.querySelector(".tbw-msg.bot:last-of-type");if(!last||last.id){var div=document.createElement("div");div.className="tbw-msg bot";msgs.appendChild(div);last=div}last.textContent=content;msgs.scrollTop=msgs.scrollHeight}
function sendMsg(question){if(isStreaming||!question.trim())return;isStreaming=true;send.disabled=true;input.disabled=true;addMsg(question,"user");input.value="";showTyping();var url=API_BASE+"/api/stream?q="+encodeURIComponent(question);var es=new EventSource(url);var botContent="";es.onmessage=function(e){var data=JSON.parse(e.data);if(data.error){botContent="Error: "+data.error;es.close();return}if(data.token){botContent+=data.token;removeTyping();updateBot(botContent)}if(data.done){es.close()}};es.onerror=function(){es.close();removeTyping();if(!botContent)updateBot("Error de conexion.");finish()};var poll=setInterval(function(){if(es.readyState===EventSource.CLOSED){clearInterval(poll);removeTyping();if(!botContent)updateBot("No se recibio respuesta.");finish()}},100);function finish(){isStreaming=false;send.disabled=false;input.disabled=false;input.focus()}}
btn.addEventListener("click",function(){panel.classList.toggle("tbw-open");btn.style.display="none";input.focus()});
close.addEventListener("click",function(){panel.classList.remove("tbw-open");btn.style.display="flex"});
send.addEventListener("click",function(){sendMsg(input.value)});
input.addEventListener("keydown",function(e){if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendMsg(input.value)}});
})();