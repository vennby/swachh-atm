window.addEventListener("DOMContentLoaded", async ()=>{
  const ctx = document.getElementById('waste-chart')
  const data = {
    labels: ['Plastic', 'Paper', 'Metal', 'E-waste', 'Other'],
    datasets: [{
      label: 'Deposits',
      data: [12, 5, 7, 3, 4],
      backgroundColor: ['#10b981','#60a5fa','#f59e0b','#ec4899','#94a3b8']
    }]
  }
  new Chart(ctx, { type:'doughnut', data })
})
