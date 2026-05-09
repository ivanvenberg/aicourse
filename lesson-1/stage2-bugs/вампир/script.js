// ЗАДАНИЕ ДЛЯ КОМАНДЫ:
// 1. Найди и исправь ошибку — секция с событием не видна на странице
// 2. Измени дату события на "31 октября 2025"
// 3. Измени цену билета на ₽3 500

// Обратный отсчёт до события
const eventDate = new Date("2025-06-13T23:00:00")

function updateCountdown() {
  const now = new Date()
  const diff = eventDate - now

  if (diff <= 0) {
    document.getElementById("days").textContent = "00"
    document.getElementById("hours").textContent = "00"
    document.getElementById("minutes").textContent = "00"
    return
  }

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  document.getElementById("days").textContent = String(days).padStart(2, "0")
  document.getElementById("hours").textContent = String(hours).padStart(2, "0")
  document.getElementById("minutes").textContent = String(minutes).padStart(2, "0")
}

updateCountdown()
setInterval(updateCountdown, 1000)

// Кнопка покупки билета
document.getElementById("ticketBtn").addEventListener("click", function() {
  this.style.display = "none"
  document.getElementById("ticketConfirm").style.display = "block"
})
