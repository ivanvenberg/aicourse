// Список фактов которые появляются по очереди при нажатии
const facts = [
  "Я не могу жить без кофе ☕",
  "Была в 12 странах и хочу ещё 🌍",
  "Читаю по книге в неделю 📚",
  "Моя любимая еда — паста 🍝",
  "Учусь делать сайты прямо сейчас 🚀"
]

// Счётчик — какой факт показываем
let currentFact = 0

// Находим кнопку и вешаем на неё слушатель нажатия
document.getElementById("btn").addEventListener("click", function() {

  // Показываем текущий факт
  document.getElementById("secret").textContent = facts[currentFact]

  // Переходим к следующему факту
  currentFact = currentFact + 1

  // Если дошли до конца — начинаем сначала
  if (currentFact >= facts.length) {
    currentFact = 0
  }

})
