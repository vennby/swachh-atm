window.addEventListener("DOMContentLoaded", async ()=>{
  const res = await fetch('/api/leaderboard')
  const data = await res.json()
  const list = document.getElementById('leaderboard')
  data.forEach((u, i)=>{
    const div = document.createElement('div')
    div.className = 'bg-white rounded-xl shadow p-3 flex justify-between items-center'
    div.innerHTML = `<div class="flex items-center gap-2"><div class="text-lg font-bold text-emerald-500">${i+1}</div><div>${u.name}</div></div><div class="font-semibold">${u.points} pts</div>`
    list.appendChild(div)
  })
})
