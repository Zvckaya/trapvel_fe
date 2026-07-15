(async ()=>{
  const res = await fetch('https://chatbot-prototype-2.onrender.com/api/chat', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ message: '테스트', history:[{role:'user', content:'테스트'}] })
  });
  console.log('status', res.status);
  console.log(await res.text());
})();
