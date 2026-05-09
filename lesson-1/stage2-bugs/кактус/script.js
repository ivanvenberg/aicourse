// ЗАДАНИЕ ДЛЯ КОМАНДЫ:
// 1. Найди и исправь ошибку — кнопки "В корзину" не работают
// 2. Измени название растения месяца на "Агава голубая"
// 3. Измени цену растения месяца на ₽3 800

let cart = []
let total = 0

// Кнопка "Купить сейчас" для растения месяца
document.getElementById("buyBtn").addEventListener("click", function() {
  addToCart("Цереус гигантский", 2400)
})

// Кнопки "В корзину" для каталога
// ОШИБКА: написано ".add-btn" с точкой — но это класс, должно быть querySelectorAll
document.querySelectorAll("add-btn").forEach(function(btn) {
  btn.addEventListener("click", function() {
    const name = this.dataset.name
    const price = parseInt(this.dataset.price)
    addToCart(name, price)
    this.textContent = "✓ Добавлено"
    this.classList.add("added")
    const self = this
    setTimeout(function() {
      self.textContent = "В корзину"
      self.classList.remove("added")
    }, 1500)
  })
})

function addToCart(name, price) {
  cart.push({ name, price })
  total += price
  renderCart()
}

function renderCart() {
  const cartItems = document.getElementById("cartItems")
  const cartEmpty = document.getElementById("cartEmpty")
  const cartFooter = document.getElementById("cartFooter")

  if (cart.length === 0) {
    cartEmpty.style.display = "block"
    cartFooter.style.display = "none"
    cartItems.innerHTML = ""
    return
  }

  cartEmpty.style.display = "none"
  cartFooter.style.display = "flex"

  cartItems.innerHTML = cart.map(function(item) {
    return "<div class='cart-item'><span>" + item.name + "</span><span>₽" + item.price.toLocaleString("ru-RU") + "</span></div>"
  }).join("")

  document.getElementById("totalPrice").textContent = "₽" + total.toLocaleString("ru-RU")
}

document.getElementById("checkoutBtn").addEventListener("click", function() {
  document.getElementById("cartFooter").style.display = "none"
  document.getElementById("cartItems").innerHTML = ""
  document.getElementById("cartEmpty").style.display = "none"
  document.getElementById("successMsg").style.display = "block"
  cart = []
  total = 0
})
