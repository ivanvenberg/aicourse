// ЗАДАНИЕ ДЛЯ КОМАНДЫ:
// 1. Найди и исправь ошибку — кнопка "Забронировать" не работает
// 2. Измени название улова дня на "Сибас с травами"
// 3. Измени часы работы в header на "Ежедневно: 11:00–01:00"

// Кнопка бронирования
// ОШИБКА: написано "reserveBtn" вместо "resBtn"
document.getElementById("reserveBtn").addEventListener("click", function() {
  const name = document.getElementById("resName").value
  const phone = document.getElementById("resPhone").value
  const date = document.getElementById("resDate").value

  if (!name || !phone || !date) {
    alert("Пожалуйста, заполните все поля")
    return
  }

  document.getElementById("resConfirm").style.display = "block"
  document.getElementById("resConfirm").scrollIntoView({ behavior: "smooth" })
})
