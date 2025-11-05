// ================================
// Swachh ATM App.js (Clean Version)
// ================================

const API = '/api'

// ---------- Token Management ----------
function setToken(t) { localStorage.setItem('sw_token', t) }
function getToken() { return localStorage.getItem('sw_token') }
function clearToken() { localStorage.removeItem('sw_token') }

// ---------- Generic Fetch with Auth ----------
async function apiFetch(path, opts = {}) {
  const headers = opts.headers || {}
  if (getToken()) headers['Authorization'] = 'Bearer ' + getToken()
  opts.headers = Object.assign({ 'Content-Type': 'application/json' }, headers)
  const r = await fetch(API + path, opts)
  if (r.status === 401) { showAuthModal(); return null }
  return r.json()
}

// ---------- DOM References ----------
const authModal = document.getElementById('auth-modal')
const authTitle = document.getElementById('auth-title')
const authSwitch = document.getElementById('auth-switch')
const authForm = document.getElementById('auth-form')
const btnLogin = document.getElementById('btn-login')

// ---------- Auth Mode Toggle ----------
let mode = 'login'
authSwitch.addEventListener('click', () => {
  mode = mode === 'login' ? 'register' : 'login'
  authTitle.textContent = mode === 'login' ? 'Login' : 'Register'
  authForm.querySelector('#auth-submit').textContent = mode === 'login' ? 'Login' : 'Register'
  authSwitch.innerHTML = mode === 'login'
    ? `No account? <button type="button" class="text-emerald-600">Register</button>`
    : `Have an account? <button type="button" class="text-emerald-600">Login</button>`
})

// ---------- Show/Hide Auth Modal ----------
function showAuthModal() { authModal.classList.remove('hidden') }
function hideAuthModal() { authModal.classList.add('hidden') }

// ---------- Handle Auth Form ----------
authForm.addEventListener('submit', async (e) => {
  e.preventDefault()
  const phone = document.getElementById('auth-phone').value.trim()
  const password = document.getElementById('auth-pass').value.trim()
  if (!phone || !password) return alert('Please fill in both fields.')

  const endpoint = mode === 'login' ? '/login' : '/register'
  const body = mode === 'login' ? { phone, password } : { name: 'User', phone, password }

  try {
    const res = await fetch(API + endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    const data = await res.json()

    if (data.access_token) {
      setToken(data.access_token)
      hideAuthModal()
      btnLogin.textContent = 'Logout'
      btnLogin.onclick = logout
      alert(mode === 'login' ? 'Welcome back!' : 'Account created!')
      loadProfile()
    } else {
      alert(data.detail || 'Error occurred.')
    }
  } catch (err) {
    console.error(err)
    alert('Connection error.')
  }
})

// ---------- Logout ----------
function logout() {
  clearToken()
  alert('Logged out')
  btnLogin.textContent = 'Login'
  btnLogin.onclick = showAuthModal
  document.getElementById('my-points').innerText = '0'
  document.getElementById('transactions-list').innerHTML = ''
  document.getElementById('leaderboard-list').innerHTML = ''
}

// ---------- Attach Auth Button ----------
btnLogin.addEventListener('click', showAuthModal)

// ---------- Deposit Flow ----------
document.getElementById('btn-scan').addEventListener('click', async () => {
  if (!getToken()) { showAuthModal(); return }

  const machine_id = prompt('Machine ID (optional)') || ''
  const waste_type = prompt('Waste type (plastic, paper, metal, ewaste, other)', 'plastic')
  const weight = parseFloat(prompt('Weight (kg)', '0.5')) || 0.5

  const body = { machine_id, waste_type, weight_kg: weight }

  const res = await fetch(API + '/deposit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + getToken()
    },
    body: JSON.stringify(body)
  })

  const data = await res.json()
  if (data.points_earned) {
    document.getElementById('my-points').innerText = data.new_total
    document.getElementById('recent-deposit').innerText = `+${data.points_earned} pts`
    alert(`Deposit successful! +${data.points_earned} pts`)
    loadProfile()
  } else {
    alert(data.detail || 'Error making deposit.')
  }
})

// ---------- Leaderboard & Transactions ----------
document.getElementById('btn-refresh').addEventListener('click', loadProfile)

async function loadProfile() {
  // Leaderboard
  const lb = await apiFetch('/leaderboard')
  if (lb) {
    const list = document.getElementById('leaderboard-list')
    list.innerHTML = ''
    lb.forEach((u, idx) => {
      const li = document.createElement('li')
      li.className = 'flex items-center justify-between bg-slate-50 p-3 rounded-lg'
      li.innerHTML = `
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-white flex items-center justify-center">${idx + 1}</div>
          <div>
            <div class="font-medium">${u.name}</div>
            <div class="text-xs text-slate-500">${u.id.slice(0, 6)}</div>
          </div>
        </div>
        <div class="font-semibold">${u.points}</div>
      `
      list.appendChild(li)
    })
  }

  // Transactions
  const txs = await apiFetch('/transactions')
  if (txs) {
    const txlist = document.getElementById('transactions-list')
    txlist.innerHTML = ''
    txs.forEach(t => {
      const li = document.createElement('li')
      li.className = 'flex justify-between bg-slate-50 p-2 rounded'
      li.innerHTML = `
        <div>${t.waste_type} • ${t.weight_kg} kg</div>
        <div class='text-emerald-600 font-semibold'>+${t.points_earned}</div>
      `
      txlist.appendChild(li)
    })
  }
}

// ---------- Init on Load ----------
if (getToken()) {
  btnLogin.textContent = 'Logout'
  btnLogin.onclick = logout
  loadProfile()
}

