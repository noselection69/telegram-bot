// Telegram Web App API
const tg = window.Telegram.WebApp;

// Инициализация
let userId = null;

// Функция для форматирования цен (1000000 -> 1.000.000)
function formatPrice(price) {
    return Number(price).toLocaleString('ru-RU');
}

// Функция переключения темы
function toggleTheme() {
    const body = document.body;
    const isDark = !body.classList.contains('light-theme');
    const themeToggle = document.getElementById('themeToggle');
    
    if (isDark) {
        body.classList.add('light-theme');
        localStorage.setItem('theme', 'light');
        themeToggle.textContent = '🌙';
    } else {
        body.c            carsList2.innerHTML = data.cars.map(car => `
                <div class="item-card">
                    <h4>${car.name}</h4>
                    <p class="item-price">💰 ${formatPrice(car.cost)}$</p>
                    <button class="btn btn-small btn-danger" onclick="deleteCar(${car.id})">🗑️ Удалить</button>
                </div>
            `).join('');t.remove('light-theme');
        localStorage.setItem('theme', 'dark');
        themeToggle.textContent = '☀️';
    }
}

// Функция загрузки сохраненной темы
function loadSavedTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    const themeToggle = document.getElementById('themeToggle');
    
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        themeToggle.textContent = '🌙';
    } else {
        document.body.classList.remove('light-theme');
        themeToggle.textContent = '☀️';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Загружаем сохраненную тему
    loadSavedTheme();
    
    // Инициализируем Telegram Web App
    tg.ready();
    tg.expand();
    
    // Получаем ID пользователя
    userId = tg.initDataUnsafe?.user?.id || 0;
    
    // Для отладки - если userId = 0, используем ID из Telegram параметров
    if (!userId && tg.initData) {
        // Пытаемся парсить initData
        const params = new URLSearchParams(tg.initData);
        const userParam = params.get('user');
        if (userParam) {
            try {
                const userData = JSON.parse(userParam);
                userId = userData.id;
            } catch(e) {
                console.warn('Failed to parse user from initData:', e);
            }
        }
    }
    
    // Если всё ещё нет userId, используем тестовый ID
    if (!userId) {
        userId = 123456789; // Тестовый ID для отладки
        console.warn('⚠️ Using test user ID:', userId);
    }
    
    console.log('🔍 Telegram Web App initialized');
    console.log('User ID:', userId);
    console.log('User:', tg.initDataUnsafe?.user);
    
    if (userId) {
        document.getElementById('userName').textContent = `👤 ${tg.initDataUnsafe.user.first_name}`;
    } else {
        console.warn('⚠️ User ID is 0 - not in Telegram Web App!');
    }
    
    // Установка цвета темы
    tg.setHeaderColor('#667eea');
    tg.setBackgroundColor('#ffffff');
    
    // Обработчик кнопки переключения темы
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Навигация по вкладкам
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchTab(tabName);
        });
    });
    
    // Загрузка данных
    loadItems();
    loadCars();
});

// Переключение вкладок
function switchTab(tabName) {
    // Скрываем все вкладки
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Удаляем активный класс со всех кнопок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Показываем нужную вкладку
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

// === ТОВАРЫ ===

function showAddItemForm() {
    document.getElementById('addItemForm').classList.remove('hidden');
    document.getElementById('addItemForm').scrollIntoView({ behavior: 'smooth' });
}

function hideAddItemForm() {
    document.getElementById('addItemForm').classList.add('hidden');
}

async function submitAddItem(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('itemName').value,
        category: document.getElementById('itemCategory').value,
        price: parseFloat(document.getElementById('itemPrice').value),
        comment: document.getElementById('itemComment').value
    };
    
    try {
        const response = await fetch('/api/add-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            document.querySelector('#addItemForm form').reset();
            hideAddItemForm();
            loadItems();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

async function loadItems() {
    try {
        console.log('📦 Loading items for user:', userId);
        
        const response = await fetch('/api/get-items', {
            headers: {
                'X-User-ID': userId
            }
        });
        
        console.log('📦 Response status:', response.status);
        const data = await response.json();
        console.log('📦 Response data:', data);
        
        if (data.success && data.items.length > 0) {
            document.getElementById('itemsList').innerHTML = data.items.map(item => `
                <div class="item-card">
                    <div class="item-header">
                        <h4>${item.name}</h4>
                        <button class="delete-btn" onclick="deleteItem(${item.id})" title="Удалить">✕</button>
                    </div>
                    <span class="badge ${item.sold ? 'sold' : 'unsold'}">
                        ${item.sold ? '✅ Продано' : '⏳ В наличии'}
                    </span>
                    <p class="item-category">📁 ${item.category}</p>
                    <p class="item-price">💰 ${formatPrice(item.price)}$</p>
                    <div class="btn-group">
                        ${!item.sold ? `<button class="btn btn-small" onclick="openSaleModal(${item.id}, '${item.name}', ${item.price})">💵 Продать</button>` : ''}
                    </div>
                </div>
            `).join('');
        } else {
            document.getElementById('itemsList').innerHTML = `
                <div class="empty">
                    <p>📦 Товары будут отображаться здесь</p>
                    <p style="font-size: 12px; color: #bbb;">Добавьте первый товар кнопкой выше</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading items:', error);
        document.getElementById('itemsList').innerHTML = `<div class="empty">⚠️ Ошибка загрузки</div>`;
    }
}

function sellItem(itemId) {
    const price = prompt('Введите цену продажи ($):');
    if (!price) return;
    
    submitSellItem(itemId, parseFloat(price));
}

async function submitSellItem(itemId, salePrice) {
    try {
        const response = await fetch('/api/sell-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                item_id: itemId,
                price: salePrice
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`✅ ${result.message}\n💰 Прибыль: ${result.profit}$`, 'success');
            loadItems();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

// === АВТОМОБИЛИ ===

function showAddCarForm() {
    document.getElementById('addCarForm').classList.remove('hidden');
    document.getElementById('addCarForm').scrollIntoView({ behavior: 'smooth' });
}

function hideAddCarForm() {
    document.getElementById('addCarForm').classList.add('hidden');
}

async function submitAddCar(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('carName').value,
        cost: parseFloat(document.getElementById('carCost').value)
    };
    
    try {
        const response = await fetch('/api/add-car', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            document.querySelector('#addCarForm form').reset();
            hideAddCarForm();
            loadCars();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

async function loadCars() {
    try {
        const response = await fetch('/api/get-cars', {
            headers: {
                'X-User-ID': userId
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.cars.length > 0) {
            document.getElementById('carsList').innerHTML = data.cars.map(car => `
                <div class="car-card">
                    <h4>${car.name}</h4>
                    <p class="car-cost">💰 ${formatPrice(car.cost)}$</p>
                    <button class="btn btn-small" onclick="openRentalModal(${car.id}, '${car.name}')">💼 Сдать в аренду</button>
                </div>
            `).join('');
        } else {
            document.getElementById('carsList').innerHTML = `
                <div class="empty">
                    <p>🚗 Автомобили будут отображаться здесь</p>
                    <p style="font-size: 12px; color: #bbb;">Добавьте первый автомобиль кнопкой выше</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading cars:', error);
        document.getElementById('carsList').innerHTML = `<div class="empty">⚠️ Ошибка загрузки</div>`;
    }
}

function showRentalModal(carId) {
    document.getElementById('rentalCarId').value = carId;
    document.getElementById('rentalModal').classList.remove('hidden');
    document.getElementById('rentalModal').style.display = 'flex';
    // Фокусируемся на первый input
    setTimeout(() => {
        document.getElementById('rentalPrice').focus();
    }, 100);
}

function openRentalModal(carId, carName) {
    showRentalModal(carId);
}

function openSaleModal(itemId, itemName, itemPrice) {
    const price = prompt(`💵 Введите цену продажи "${itemName}" (куплено за ${itemPrice}$):`, itemPrice);
    if (!price) return;
    submitSellItem(itemId, parseFloat(price));
}

async function deleteCar(carId) {
    if (confirm('Вы уверены? Это удалит машину и все связанные с ней аренды.')) {
        try {
            const response = await fetch(`/api/delete-car/${carId}`, {
                method: 'DELETE',
                headers: {'X-User-ID': userId}
            });
            
            const data = await response.json();
            if (data.success) {
                showNotification('Машина удалена', 'success');
                loadCars();
                loadCarsForView();
            } else {
                showNotification(data.error || 'Ошибка удаления', 'error');
            }
        } catch (error) {
            showNotification('Ошибка удаления: ' + error.message, 'error');
        }
    }
}

async function deleteItem(itemId) {
    if (confirm('Вы уверены? Это удалит товар.')) {
        try {
            const response = await fetch(`/api/delete-item/${itemId}`, {
                method: 'DELETE',
                headers: {'X-User-ID': userId}
            });
            
            const data = await response.json();
            if (data.success) {
                showNotification('Товар удалён', 'success');
                loadItems();
            } else {
                showNotification(data.error || 'Ошибка удаления', 'error');
            }
        } catch (error) {
            showNotification('Ошибка удаления: ' + error.message, 'error');
        }
    }
}

function closeRentalModal() {
    const modal = document.getElementById('rentalModal');
    modal.classList.add('hidden');
    modal.style.display = 'none';
    document.querySelector('#rentalModal form').reset();
}

async function submitRental(event) {
    event.preventDefault();
    
    const data = {
        car_id: parseInt(document.getElementById('rentalCarId').value),
        price_per_hour: parseFloat(document.getElementById('rentalPrice').value),
        hours: parseInt(document.getElementById('rentalHours').value),
        end_time: document.getElementById('rentalEndTime').value
    };
    
    try {
        const response = await fetch('/api/rent-car', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            closeRentalModal();
            loadCars();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

// === УТИЛИТЫ ===

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    
    // Автоскрытие через 3 секунды
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}

// Отправка данных в основной бот (для закрытия Web App)
function closeWebApp(message = '') {
    tg.sendData(JSON.stringify({
        action: 'close',
        message: message
    }));
}

// === ИНВЕНТАРЬ, СТАТИСТИКА, ИСТОРИЯ ===

function showInventory() {
    const inv = document.getElementById('inventoryView');
    if (inv.classList.contains('hidden')) {
        document.getElementById('addItemForm').classList.add('hidden');
        inv.classList.remove('hidden');
        loadInventory();
        inv.scrollIntoView({ behavior: 'smooth' });
    } else {
        hideInventory();
    }
}

function hideInventory() {
    document.getElementById('inventoryView').classList.add('hidden');
}

async function loadInventory() {
    const inventoryList = document.getElementById('inventoryList');
    inventoryList.innerHTML = '<p class="loading">Загрузка...</p>';
    
    try {
        const response = await fetch('/api/get-items', {
            headers: {'X-User-ID': userId}
        });
        
        const data = await response.json();
        
        if (data.success && data.items.length > 0) {
            // Фильтруем только непроданные товары
            const unsoldItems = data.items.filter(item => !item.sold);
            
            if (unsoldItems.length > 0) {
                inventoryList.innerHTML = unsoldItems.map(item => `
                    <div class="item-card">
                        <div class="item-header">
                            <h4>${item.name}</h4>
                            <button class="delete-btn" onclick="deleteItem(${item.id})" title="Удалить">✕</button>
                        </div>
                        <span class="badge unsold">⏳ В наличии</span>
                        <p class="item-category">📁 ${item.category}</p>
                        <p class="item-price">💰 ${formatPrice(item.price)}$</p>
                        <div class="btn-group">
                            <button class="btn btn-small" onclick="openSaleModal(${item.id}, '${item.name}', ${item.price})">💵 Продать</button>
                        </div>
                    </div>
                `).join('');
            } else {
                inventoryList.innerHTML = '<p class="empty">📦 Нет товаров в наличии</p>';
            }
        } else {
            inventoryList.innerHTML = '<p class="empty">📦 Товаров нет</p>';
        }
    } catch (error) {
        console.error('Error loading inventory:', error);
        inventoryList.innerHTML = '<p class="error">Ошибка загрузки</p>';
    }
}

function showStatistics() {
    const stats = document.getElementById('statisticsView');
    if (stats.classList.contains('hidden')) {
        document.getElementById('addItemForm').classList.add('hidden');
        stats.classList.remove('hidden');
        loadStatistics();
        stats.scrollIntoView({ behavior: 'smooth' });
    } else {
        hideStatistics();
    }
}

function hideStatistics() {
    document.getElementById('statisticsView').classList.add('hidden');
}

function showHistory() {
    const hist = document.getElementById('historyView');
    if (hist.classList.contains('hidden')) {
        document.getElementById('addItemForm').classList.add('hidden');
        hist.classList.remove('hidden');
        loadHistory();
        hist.scrollIntoView({ behavior: 'smooth' });
    } else {
        hideHistory();
    }
}

function hideHistory() {
    document.getElementById('historyView').classList.add('hidden');
}

// === ЦЕНЫ СКУПА ===

function showBuyPrices() {
    const buyPrices = document.getElementById('buyPricesView');
    if (buyPrices.classList.contains('hidden')) {
        document.getElementById('addItemForm').classList.add('hidden');
        buyPrices.classList.remove('hidden');
        loadBuyPrices();
        buyPrices.scrollIntoView({ behavior: 'smooth' });
    } else {
        hideBuyPrices();
    }
}

function hideBuyPrices() {
    document.getElementById('buyPricesView').classList.add('hidden');
}

async function loadBuyPrices() {
    const buyPricesList = document.getElementById('buyPricesList');
    buyPricesList.innerHTML = '<p class="loading">Загрузка...</p>';
    
    try {
        const response = await fetch('/api/get-buy-prices', {
            headers: {'X-User-ID': userId}
        });
        
        const data = await response.json();
        
        if (data.success && data.prices.length > 0) {
            buyPricesList.innerHTML = data.prices.map(price => `
                <div class="item-card">
                    <div class="item-header">
                        <h4>${price.item_name}</h4>
                        <button class="delete-btn" onclick="deleteBuyPrice(${price.id})" title="Удалить">✕</button>
                    </div>
                    <p class="item-price">💰 ${formatPrice(price.price)}$</p>
                    <p class="small" style="color: var(--text-secondary); margin-top: 4px;">📅 ${new Date(price.created_at).toLocaleString('ru-RU')}</p>
                </div>
            `).join('');
        } else {
            buyPricesList.innerHTML = '<p class="empty">💰 Цены не добавлены</p>';
        }
    } catch (error) {
        console.error('Error loading buy prices:', error);
        buyPricesList.innerHTML = '<p class="error">Ошибка загрузки</p>';
    }
}

async function submitBuyPrice() {
    const name = document.getElementById('itemNameInput').value.trim();
    const price = document.getElementById('itemPriceInput').value;
    
    if (!name || !price) {
        showNotification('Заполните оба поля', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/add-buy-price', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId
            },
            body: JSON.stringify({
                item_name: name,
                price: parseFloat(price)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Цена добавлена', 'success');
            document.getElementById('itemNameInput').value = '';
            document.getElementById('itemPriceInput').value = '';
            loadBuyPrices();
        } else {
            showNotification(data.error || 'Ошибка добавления', 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

async function deleteBuyPrice(priceId) {
    if (!confirm('Удалить эту цену?')) return;
    
    try {
        const response = await fetch(`/api/delete-buy-price/${priceId}`, {
            method: 'DELETE',
            headers: {'X-User-ID': userId}
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Цена удалена', 'success');
            loadBuyPrices();
        } else {
            showNotification(data.error || 'Ошибка удаления', 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

function searchBuyPrices() {
    const query = document.getElementById('buyPriceSearch').value.toLowerCase();
    const items = document.getElementById('buyPricesList').querySelectorAll('.item-card');
    
    items.forEach(item => {
        const name = item.querySelector('h4').textContent.toLowerCase();
        item.style.display = name.includes(query) ? 'block' : 'none';
    });
}

function loadStatistics() {
    const statsContent = document.getElementById('statisticsContent');
    statsContent.innerHTML = '<p class="loading">Загрузка статистики...</p>';
    
    fetch('/api/get-sales', {
        headers: {
            'X-User-ID': userId
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            const items_count = data.total_sales;
            const content = `
                <div class="stats-container">
                    <div class="stat-item">
                        <span class="stat-label">Всего продано товаров:</span>
                        <span class="stat-value">${items_count}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Общий доход:</span>
                        <span class="stat-value">${formatPrice(data.total_income)}$</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Общая прибыль:</span>
                        <span class="stat-value">${formatPrice(data.total_profit)}$</span>
                    </div>
                    ${items_count > 0 ? `
                    <div class="stat-item">
                        <span class="stat-label">Средняя прибыль на товар:</span>
                        <span class="stat-value">${formatPrice(data.total_profit / items_count)}$</span>
                    </div>
                    ` : ''}
                </div>
            `;
            statsContent.innerHTML = content;
        } else {
            statsContent.innerHTML = '<p class="error">Ошибка загрузки статистики</p>';
        }
    })
    .catch(e => {
        console.error('Error loading statistics:', e);
        statsContent.innerHTML = '<p class="error">Ошибка загрузки</p>';
    });
}

function loadHistory() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '<p class="loading">Загрузка истории...</p>';
    
    fetch('/api/get-sales', {
        headers: {
            'X-User-ID': userId
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success && data.sales.length > 0) {
            historyList.innerHTML = data.sales.map(sale => `
                <div class="item-card">
                    <h4>${sale.item_name}</h4>
                    <p>💵 Продано за: <strong>${formatPrice(sale.sale_price)}$</strong></p>
                    <p>💰 Куплено за: ${formatPrice(sale.purchase_price)}$</p>
                    <p class="profit ${sale.profit >= 0 ? 'positive' : 'negative'}">
                        📈 Прибыль: ${sale.profit >= 0 ? '+' : ''}${formatPrice(sale.profit)}$
                    </p>
                    <p class="small">📅 ${new Date(sale.created_at).toLocaleString('ru-RU')}</p>
                </div>
            `).join('');
        } else {
            historyList.innerHTML = '<p class="empty">История продаж пуста</p>';
        }
    })
    .catch(e => {
        console.error('Error loading history:', e);
        historyList.innerHTML = '<p class="error">Ошибка загрузки</p>';
    });
}

// === АРЕНДА ===

function showCars() {
    const cars = document.getElementById('carsView');
    if (cars.classList.contains('hidden')) {
        document.getElementById('addCarForm').classList.add('hidden');
        cars.classList.remove('hidden');
        loadCarsForView();
        cars.scrollIntoView({ behavior: 'smooth' });
    } else {
        hideCars();
    }
}

function hideCars() {
    document.getElementById('carsView').classList.add('hidden');
}

function showRentalStats() {
    const stats = document.getElementById('rentalStatsView');
    if (stats.classList.contains('hidden')) {
        document.getElementById('addCarForm').classList.add('hidden');
        stats.classList.remove('hidden');
        loadRentalStats();
        stats.scrollIntoView({ behavior: 'smooth' });
    } else {
        hideRentalStats();
    }
}

function hideRentalStats() {
    document.getElementById('rentalStatsView').classList.add('hidden');
}

function showActiveRentals() {
    const active = document.getElementById('activeRentalsView');
    if (active.classList.contains('hidden')) {
        document.getElementById('addCarForm').classList.add('hidden');
        active.classList.remove('hidden');
        loadActiveRentals();
        active.scrollIntoView({ behavior: 'smooth' });
    } else {
        hideActiveRentals();
    }
}

function hideActiveRentals() {
    document.getElementById('activeRentalsView').classList.add('hidden');
}

function loadCarsForView() {
    // Загружаем авто для просмотра (НЕ дублируем)
    const carsList2 = document.getElementById('carsList2');
    carsList2.innerHTML = '<p class="loading">Загрузка...</p>';
    
    fetch('/api/get-cars', {
        headers: {'X-User-ID': userId}
    })
    .then(r => r.json())
    .then(data => {
        if (data.success && data.cars.length > 0) {
            carsList2.innerHTML = data.cars.map(car => `
                <div class="item-card">
                    <div class="item-header">
                        <h4>${car.name}</h4>
                        <button class="delete-btn" onclick="deleteCar(${car.id})" title="Удалить">✕</button>
                    </div>
                    <p class="item-price">💰 ${formatPrice(car.cost)}$</p>
                </div>
            `).join('');
        } else {
            carsList2.innerHTML = '<p class="empty">Авто не добавлены</p>';
        }
    })
    .catch(err => {
        carsList2.innerHTML = '<p class="error">Ошибка загрузки</p>';
    });
}

function loadRentalStats() {
    const statsContent = document.getElementById('rentalStatsContent');
    statsContent.innerHTML = '<p class="loading">Загрузка статистики...</p>';
    
    fetch('/api/get-rental-stats', {
        headers: {'X-User-ID': userId}
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            const content = `
                <div class="stats-container">
                    <div class="stat-item">
                        <span class="stat-label">Всего авто:</span>
                        <span class="stat-value">${data.total_cars}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Всего аренд:</span>
                        <span class="stat-value">${data.total_rentals}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Общий доход:</span>
                        <span class="stat-value">${formatPrice(data.total_income)}$</span>
                    </div>
                    ${data.total_rentals > 0 ? `
                    <div class="stat-item">
                        <span class="stat-label">Средний доход на аренду:</span>
                        <span class="stat-value">${formatPrice(data.total_income / data.total_rentals)}$</span>
                    </div>
                    ` : ''}
                </div>
            `;
            statsContent.innerHTML = content;
        } else {
            statsContent.innerHTML = '<p class="error">Ошибка загрузки</p>';
        }
    })
    .catch(e => {
        console.error('Error loading rental stats:', e);
        statsContent.innerHTML = '<p class="error">Ошибка загрузки</p>';
    });
}

function loadActiveRentals() {
    const activeList = document.getElementById('activeRentalsList');
    activeList.innerHTML = '<p class="loading">Загрузка...</p>';
    
    fetch('/api/get-rentals', {
        headers: {'X-User-ID': userId}
    })
    .then(r => r.json())
    .then(data => {
        if (data.success && data.rentals.length > 0) {
            activeList.innerHTML = data.rentals.map(rental => `
                <div class="item-card">
                    <h4>${rental.car_name}</h4>
                    <p>⏰ ${rental.hours}ч × ${formatPrice(rental.price_per_hour)}$ = <strong>${formatPrice(rental.total_income)}$</strong></p>
                    <p class="small">🕐 ${new Date(rental.rental_start).toLocaleString('ru-RU')}</p>
                    <p class="small">🕑 ${new Date(rental.rental_end).toLocaleString('ru-RU')}</p>
                </div>
            `).join('');
        } else {
            activeList.innerHTML = '<p class="empty">Активных аренд нет</p>';
        }
    })
    .catch(err => {
        activeList.innerHTML = '<p class="error">Ошибка загрузки</p>';
    });
}
