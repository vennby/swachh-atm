const API = '/api'

function setToken(t){ localStorage.setItem('sw_token', t) }
function getToken(){ return localStorage.getItem('sw_token') }

async function apiFetch(path, opts={}){
  const headers = opts.headers || {};
  if(getToken()) headers['Authorization'] = 'Bearer ' + getToken();
  opts.headers = Object.assign({'Content-Type':'application/json'}, headers)
  const r = await fetch(API + path, opts)
  if(r.status === 401){ alert('Please login'); return null }
  return r.json()
}

// login/register quick UI flows
document.getElementById('btn-login').addEventListener('click', async ()=>{
  const phone = prompt('Phone number (for prototype)')
  if(!phone) return
  const pw = prompt('Pick a password')
  if(!pw) return
  const res = await fetch('/api/register', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name:'User', phone, password: pw})})
  const data = await res.json()
  if(data.access_token) { setToken(data.access_token); alert('Registered & logged in!'); loadProfile(); }
  else alert(JSON.stringify(data))
})

async function loadProfile(){
  // fetch leaderboard & transactions
  const lb = await apiFetch('/leaderboard')
  if(lb){
    const list = document.getElementById('leaderboard-list'); list.innerHTML = '';
    lb.forEach((u, idx)=>{
      const li = document.createElement('li');
      li.className = 'flex items-center justify-between bg-slate-50 p-3 rounded-lg'
      li.innerHTML = `<div class="flex items-center gap-3"><div class="w-8 h-8 rounded-full bg-white flex items-center justify-center">${idx+1}</div><div><div class="font-medium">${u.name}</div><div class="text-xs text-slate-500">${u.id.slice(0,6)}</div></div></div><div class="font-semibold">${u.points}</div>`
      list.appendChild(li)
    })
  }
  const txs = await apiFetch('/transactions')
  if(txs){
    const txlist = document.getElementById('transactions-list'); txlist.innerHTML=''
    txs.forEach(t=>{
      const li = document.createElement('li'); li.className='flex justify-between'
      li.innerHTML = `<div>${t.waste_type} • ${t.weight_kg} kg</div><div class='text-slate-500'>+${t.points_earned}</div>`
      txlist.appendChild(li)
    })
  }
}

// Simulate deposit flow
document.getElementById('btn-scan').addEventListener('click', async ()=>{
  if(!getToken()){ alert('Please login first'); return }
  const machine_id = prompt('Machine ID to simulate (or leave empty to auto-generate)') || ''
  const waste_type = prompt('Waste type (plastic, paper, metal, ewaste, other)','plastic')
  const weight = parseFloat(prompt('Weight (kg)', '0.5')) || 0.5
  const body = { machine_id, waste_type, weight_kg: weight }
  const res = await fetch('/api/deposit', {method:'POST', headers: {'Content-Type':'application/json', 'Authorization': 'Bearer ' + getToken()}, body: JSON.stringify(body)})
  const data = await res.json()
  if(data && data.points_earned){
    document.getElementById('my-points').innerText = data.new_total
    document.getElementById('recent-deposit').innerText = `+${data.points_earned} pts`;
    alert(`Deposit successful! +${data.points_earned} pts`)
    loadProfile()
  } else {
    alert(JSON.stringify(data))
  }
})

// refresh leaderboard button
document.getElementById('btn-refresh').addEventListener('click', loadProfile)

// initial load
setTimeout(()=>{ if(getToken()) loadProfile() }, 500)