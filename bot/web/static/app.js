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
        body.classList.remove('light-theme');
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
    
    // Инициализация обработчиков для полей цены скупа
    const nameInput = document.getElementById('itemNameInput');
    const priceInput = document.getElementById('itemPriceInput');
    
    if (nameInput) {
        nameInput.addEventListener('focus', () => enableBuyPriceInputs());
        nameInput.addEventListener('click', () => enableBuyPriceInputs());
        nameInput.addEventListener('input', () => enableBuyPriceInputs());
    }
    
    if (priceInput) {
        priceInput.addEventListener('focus', () => enableBuyPriceInputs());
        priceInput.addEventListener('click', () => enableBuyPriceInputs());
        priceInput.addEventListener('input', () => enableBuyPriceInputs());
    }
    
    // Постоянный мониторинг состояния input'ов (каждые 500ms проверяем их активность)
    setInterval(() => {
        const nameInput = document.getElementById('itemNameInput');
        const priceInput = document.getElementById('itemPriceInput');
        
        if (nameInput && priceInput) {
            // Проверяем не заблокированы ли они
            if (nameInput.disabled || priceInput.disabled ||
                getComputedStyle(nameInput).pointerEvents === 'none' ||
                getComputedStyle(priceInput).pointerEvents === 'none' ||
                parseFloat(getComputedStyle(nameInput).opacity) < 0.5 ||
                parseFloat(getComputedStyle(priceInput).opacity) < 0.5) {
                console.warn('⚠️ Buy price inputs detected as blocked, recovering...');
                enableBuyPriceInputs();
            }
        }
    }, 500);
    
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
    
    // Закрываем все popup view'ы (статистика, история, цены скупа и т.д.)
    document.getElementById('statisticsView')?.classList.add('hidden');
    document.getElementById('historyView')?.classList.add('hidden');
    document.getElementById('buyPricesView')?.classList.add('hidden');
    document.getElementById('addItemForm')?.classList.add('hidden');
    
    // Удаляем активный класс со всех кнопок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Показываем нужную вкладку
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
    
    // Загружаем данные для вкладки
    if (tabName === 'inventory') {
        loadInventory();
    } else if (tabName === 'items') {
        loadItems();
    }
}

// Функция для закрытия всех popup view'ов
function closeAllPopups() {
    const popups = [
        'addItemForm',
        'addCarForm',
        'statisticsView',
        'historyView',
        'buyPricesView',
        'rentalModal',
        'carsView',
        'rentalStatsView',
        'activeRentalsView'
    ];
    
    popups.forEach(popupId => {
        const element = document.getElementById(popupId);
        if (element) {
            element.classList.add('hidden');
        }
    });
}

// === ТОВАРЫ ===

function showAddItemForm() {
    closeAllPopups();
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
            loadInventory();
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
            // Показываем только ПРОДАННЫЕ товары (история продаж)
            const soldItems = data.items.filter(item => item.sold);
            
            if (soldItems.length > 0) {
                document.getElementById('itemsList').innerHTML = soldItems.map(item => `
                    <div class="item-card">
                        <div class="item-header">
                            <h4>${item.name}</h4>
                            <button class="delete-btn" onclick="deleteItem(${item.id})" title="Удалить">✕</button>
                        </div>
                        <span class="badge sold">✅ Продано</span>
                        <p class="item-category">📁 ${item.category}</p>
                        <p class="item-price">💰 ${formatPrice(item.price)}$</p>
                    </div>
                `).join('');
            } else {
                document.getElementById('itemsList').innerHTML = `
                    <div class="empty">
                        <p>� История продаж пуста</p>
                    </div>
                `;
            }
        } else if (data.success) {
            // Товары не добавлены или ошибка загрузки - просто очищаем список
            document.getElementById('itemsList').innerHTML = '';
        } else {
            // Ошибка API
            document.getElementById('itemsList').innerHTML = `<div class="empty">⚠️ Ошибка загрузки: ${data.error || 'Неизвестная ошибка'}</div>`;
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
            loadInventory();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

// === АВТОМОБИЛИ ===

function showAddCarForm() {
    closeAllPopups();
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
    document.getElementById('rentalPastToggle').checked = false;  // Сбрасываем чекбокс
    document.getElementById('rentalModal').classList.remove('hidden');
    document.getElementById('rentalModal').style.display = 'flex';
    // Сбрасываем поле end_time в нормальное состояние
    const endTimeInput = document.getElementById('rentalEndTime');
    endTimeInput.disabled = false;
    endTimeInput.placeholder = '22:30 или +4';
    endTimeInput.setAttribute('required', 'required');
    document.getElementById('rentalEndTimeLabel').textContent = 'Время окончания (HH:MM или +N часов):';
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

function editRental(rentalId, price, hours, carName) {
    document.getElementById('editRentalId').value = rentalId;
    document.getElementById('editRentalCar').value = carName;
    document.getElementById('editRentalPrice').value = price;
    document.getElementById('editRentalHours').value = hours;
    updateEditRentalSum();
    
    document.getElementById('editRentalModal').classList.remove('hidden');
    document.getElementById('editRentalModal').style.display = 'flex';
    
    setTimeout(() => {
        document.getElementById('editRentalPrice').focus();
    }, 100);
}

function closeEditRentalModal() {
    const modal = document.getElementById('editRentalModal');
    modal.classList.add('hidden');
    modal.style.display = 'none';
}

function updateEditRentalSum() {
    const price = parseFloat(document.getElementById('editRentalPrice').value) || 0;
    const hours = parseInt(document.getElementById('editRentalHours').value) || 0;
    const sum = price * hours;
    document.getElementById('editRentalNewSum').textContent = formatPrice(sum);
}

async function submitEditRental(event) {
    event.preventDefault();
    
    const rentalId = document.getElementById('editRentalId').value;
    const price = parseFloat(document.getElementById('editRentalPrice').value);
    const hours = parseInt(document.getElementById('editRentalHours').value);
    
    try {
        const response = await fetch(`/api/edit-rental/${rentalId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId
            },
            body: JSON.stringify({
                price_per_hour: price,
                hours: hours
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Аренда обновлена!', 'success');
            closeEditRentalModal();
            loadActiveRentals();
            loadCarsForView();
            loadRentalStats();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

function toggleRentalPast() {
    const isPast = document.getElementById('rentalPastToggle').checked;
    const endTimeInput = document.getElementById('rentalEndTime');
    const label = document.getElementById('rentalEndTimeLabel');
    
    if (isPast) {
        endTimeInput.disabled = true;
        endTimeInput.value = '';
        endTimeInput.placeholder = 'Не требуется (прошлая аренда)';
        endTimeInput.removeAttribute('required');
        label.textContent = 'Время окончания (не требуется):';
    } else {
        endTimeInput.disabled = false;
        endTimeInput.placeholder = '22:30 или +4';
        endTimeInput.setAttribute('required', 'required');
        label.textContent = 'Время окончания (HH:MM или +N часов):';
    }
}

async function submitRental(event) {
    event.preventDefault();
    
    const isPast = document.getElementById('rentalPastToggle').checked;
    
    const data = {
        car_id: parseInt(document.getElementById('rentalCarId').value),
        price_per_hour: parseFloat(document.getElementById('rentalPrice').value),
        hours: parseInt(document.getElementById('rentalHours').value),
        end_time: isPast ? '' : document.getElementById('rentalEndTime').value,  // Пустое для прошлых
        is_past: isPast
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
            loadCarsForView();
            loadActiveRentals();
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
            inventoryList.innerHTML = `
                <div class="empty">
                    <p>📦 Товары будут отображаться здесь</p>
                    <p style="font-size: 12px; color: #bbb;">Добавьте первый товар кнопкой выше</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading inventory:', error);
        inventoryList.innerHTML = '<p class="error">Ошибка загрузки</p>';
    }
}

function showStatistics() {
    closeAllPopups();
    const stats = document.getElementById('statisticsView');
    stats.classList.remove('hidden');
    loadStatistics();
    stats.scrollIntoView({ behavior: 'smooth' });
}

function hideStatistics() {
    document.getElementById('statisticsView').classList.add('hidden');
}

function showHistory() {
    closeAllPopups();
    const hist = document.getElementById('historyView');
    hist.classList.remove('hidden');
    loadHistory();
    hist.scrollIntoView({ behavior: 'smooth' });
}

function hideHistory() {
    document.getElementById('historyView').classList.add('hidden');
}

// === ЦЕНЫ СКУПА ===

function enableBuyPriceInputs() {
    const nameInput = document.getElementById('itemNameInput');
    const priceInput = document.getElementById('itemPriceInput');
    
    if (nameInput) {
        // Убираем все блокирующие атрибуты и стили
        nameInput.disabled = false;
        nameInput.readOnly = false;
        nameInput.setAttribute('aria-disabled', 'false');
        
        // Очищаем все блокирующие стили
        nameInput.style.pointerEvents = 'auto';
        nameInput.style.opacity = '1';
        nameInput.style.cursor = 'text';
        nameInput.style.userSelect = 'auto';
        nameInput.style.WebkitUserSelect = 'auto';
        nameInput.style.MozUserSelect = 'auto';
        nameInput.style.msUserSelect = 'auto';
        nameInput.style.visibility = 'visible';
        nameInput.style.display = 'block';
        
        // Удаляем все классы которые могут блокировать
        nameInput.classList.remove('disabled');
        nameInput.classList.remove('readonly');
    }
    
    if (priceInput) {
        // Убираем все блокирующие атрибуты и стили
        priceInput.disabled = false;
        priceInput.readOnly = false;
        priceInput.setAttribute('aria-disabled', 'false');
        
        // Очищаем все блокирующие стили
        priceInput.style.pointerEvents = 'auto';
        priceInput.style.opacity = '1';
        priceInput.style.cursor = 'text';
        priceInput.style.userSelect = 'auto';
        priceInput.style.WebkitUserSelect = 'auto';
        priceInput.style.MozUserSelect = 'auto';
        priceInput.style.msUserSelect = 'auto';
        priceInput.style.visibility = 'visible';
        priceInput.style.display = 'block';
        
        // Удаляем все классы которые могут блокировать
        priceInput.classList.remove('disabled');
        priceInput.classList.remove('readonly');
    }
}

function showBuyPrices() {
    closeAllPopups();
    const buyPrices = document.getElementById('buyPricesView');
    buyPrices.classList.remove('hidden');
    
    // Убеждаемся что input'ы активны
    setTimeout(() => {
        enableBuyPriceInputs();
        const nameInput = document.getElementById('itemNameInput');
        if (nameInput) {
            nameInput.value = '';
            nameInput.focus();
        }
    }, 50);
    
    loadBuyPrices();
    buyPrices.scrollIntoView({ behavior: 'smooth' });
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
                    <p class="item-price">💰 ${price.price_text || formatPrice(price.price)}$</p>
                    <p class="small" style="color: var(--text-secondary); margin-top: 4px;">� ${price.seller_name}</p>
                    <p class="small" style="color: var(--text-secondary); margin-top: 2px;">�📅 ${new Date(price.created_at).toLocaleString('ru-RU')}</p>
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
    const nameInput = document.getElementById('itemNameInput');
    const priceInput = document.getElementById('itemPriceInput');
    
    const name = nameInput.value.trim();
    const priceText = priceInput.value.trim();
    
    if (!name || !priceText) {
        showNotification('Заполните оба поля', 'warning');
        return;
    }
    
    // Парсим цену - извлекаем только числа и точки для валидации
    const price = parseFloat(priceText.replace(/[^\d.]/g, ''));
    
    if (isNaN(price) || price <= 0) {
        showNotification('Цена должна быть числом > 0', 'warning');
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
                price: price,
                price_text: priceText  // Отправляем оригинальный текст
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Цена добавлена', 'success');
            // Очищаем поля
            nameInput.value = '';
            priceInput.value = '';
            // Перезагружаем список
            await loadBuyPrices();
            // Восстанавливаем состояние input'ов после загрузки
            setTimeout(() => {
                enableBuyPriceInputs();
                const freshNameInput = document.getElementById('itemNameInput');
                if (freshNameInput) {
                    freshNameInput.value = '';
                    freshNameInput.focus();
                }
            }, 100);
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

function loadStatistics(timeFilter = 'all', dealFilter = 'all') {
    const statsContent = document.getElementById('statisticsContent');
    statsContent.innerHTML = '<p class="loading">Загрузка статистики...</p>';
    
    // Обновляем активные кнопки фильтров
    document.getElementById('filterDay').style.background = timeFilter === 'day' ? 'var(--accent-color)' : 'var(--btn-bg)';
    document.getElementById('filterWeek').style.background = timeFilter === 'week' ? 'var(--accent-color)' : 'var(--btn-bg)';
    document.getElementById('filterAll').style.background = timeFilter === 'all' ? 'var(--accent-color)' : 'var(--btn-bg)';
    
    document.getElementById('filterBest').style.background = dealFilter === 'best' ? 'var(--success-color)' : 'var(--btn-bg)';
    document.getElementById('filterWorst').style.background = dealFilter === 'worst' ? 'var(--danger-color)' : 'var(--btn-bg)';
    document.getElementById('filterNone').style.background = dealFilter === 'all' ? 'var(--btn-bg)' : 'var(--btn-bg)';
    
    const params = new URLSearchParams();
    if (timeFilter !== 'all') params.append('time_filter', timeFilter);
    if (dealFilter !== 'all') params.append('deal_filter', dealFilter);
    
    const url = '/api/get-sales' + (params.toString() ? '?' + params.toString() : '');
    
    fetch(url, {
        headers: {
            'X-User-ID': userId
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            const items_count = data.total_sales;
            const timeLabel = timeFilter === 'day' ? 'за день' : timeFilter === 'week' ? 'за неделю' : 'всё время';
            const dealLabel = dealFilter === 'best' ? ' (выгодные)' : dealFilter === 'worst' ? ' (невыгодные)' : '';
            
            const content = `
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 15px; padding: 10px; background: var(--bg-secondary); border-radius: 6px;">
                    📊 Фильтр: ${timeLabel}${dealLabel}
                </div>
                <div class="stats-container">
                    <div class="stat-item">
                        <span class="stat-label">Продано товаров:</span>
                        <span class="stat-value">${items_count}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Общий доход:</span>
                        <span class="stat-value">${formatPrice(data.total_income)}$</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Общая прибыль:</span>
                        <span class="stat-value" style="color: ${data.total_profit >= 0 ? 'var(--success-color)' : 'var(--danger-color)'};">${data.total_profit >= 0 ? '+' : ''}${formatPrice(data.total_profit)}$</span>
                    </div>
                    ${items_count > 0 ? `
                    <div class="stat-item">
                        <span class="stat-label">Средняя прибыль на товар:</span>
                        <span class="stat-value" style="color: ${data.total_profit / items_count >= 0 ? 'var(--success-color)' : 'var(--danger-color)'};">${data.total_profit / items_count >= 0 ? '+' : ''}${formatPrice(data.total_profit / items_count)}$</span>
                    </div>
                    ` : ''}
                </div>
                ${items_count > 0 ? `
                <div style="margin-top: 15px;">
                    <h4 style="margin-bottom: 10px;">Товары (${items_count}):</h4>
                    <div style="max-height: 400px; overflow-y: auto;">
                        ${data.sales.map((sale, idx) => `
                            <div style="padding: 8px; background: var(--bg-secondary); margin-bottom: 8px; border-radius: 4px; border-left: 3px solid ${sale.profit >= 0 ? 'var(--success-color)' : 'var(--danger-color)'};">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="flex: 1;"><strong>${sale.item_name}</strong></span>
                                    <span style="color: ${sale.profit >= 0 ? 'var(--success-color)' : 'var(--danger-color)'}; font-weight: bold;">${sale.profit >= 0 ? '+' : ''}${formatPrice(sale.profit)}$</span>
                                </div>
                                <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">
                                    Куплено: ${formatPrice(sale.purchase_price)}$ → Продано: ${formatPrice(sale.sale_price)}$
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : '<p class="empty">📊 Нет данных для отображения</p>'}
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
    closeAllPopups();
    const cars = document.getElementById('carsView');
    cars.classList.remove('hidden');
    loadCarsForView();
    cars.scrollIntoView({ behavior: 'smooth' });
}

function hideCars() {
    document.getElementById('carsView').classList.add('hidden');
}

function showRentalStats() {
    closeAllPopups();
    const stats = document.getElementById('rentalStatsView');
    stats.classList.remove('hidden');
    loadRentalStats();
    stats.scrollIntoView({ behavior: 'smooth' });
}

function hideRentalStats() {
    document.getElementById('rentalStatsView').classList.add('hidden');
}

function showActiveRentals() {
    closeAllPopups();
    const active = document.getElementById('activeRentalsView');
    active.classList.remove('hidden');
    loadActiveRentals();
    active.scrollIntoView({ behavior: 'smooth' });
}

function hideActiveRentals() {
    document.getElementById('activeRentalsView').classList.add('hidden');
}

function loadCarsForView() {
    // Загружаем авто для просмотра с окупаемостью
    const carsList2 = document.getElementById('carsList2');
    carsList2.innerHTML = '<p class="loading">Загрузка...</p>';
    
    fetch('/api/get-cars', {
        headers: {'X-User-ID': userId}
    })
    .then(r => r.json())
    .then(data => {
        if (data.success && data.cars.length > 0) {
            carsList2.innerHTML = data.cars.map(car => {
                const paybackColor = car.payback_percent >= 100 ? '#4caf50' : 
                                    car.payback_percent >= 50 ? '#ff9800' : '#f44336';
                return `
                    <div class="item-card">
                        <div class="item-header">
                            <h4>${car.name}</h4>
                            <button class="delete-btn" onclick="deleteCar(${car.id})" title="Удалить">✕</button>
                        </div>
                        <p class="item-price">💰 Стоимость: ${formatPrice(car.cost)}$</p>
                        <p class="item-price">📊 Доход: ${formatPrice(car.total_income)}$</p>
                        <div class="payback-bar">
                            <div class="payback-fill" style="width: ${Math.min(100, car.payback_percent)}%; background-color: ${paybackColor};"></div>
                        </div>
                        <p class="payback-text">🎯 Окупилось: ${car.payback_percent}% (${car.rentals_count} аренд)</p>
                    </div>
                `;
            }).join('');
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
    const timeFilter = document.getElementById('rentalTimeFilter')?.value || 'all';
    
    statsContent.innerHTML = '<p class="loading">Загрузка статистики...</p>';
    
    fetch(`/api/get-rental-stats?time_filter=${timeFilter}`, {
        headers: {'X-User-ID': userId}
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            let carsTableHtml = '';
            
            if (data.cars_stats && data.cars_stats.length > 0) {
                carsTableHtml = `
                    <div class="stats-section">
                        <h4>📊 Статистика по автомобилям:</h4>
                        <div class="cars-stats-table">
                            ${data.cars_stats.map(car => `
                                <div class="car-stat-item">
                                    <div class="car-stat-header">
                                        <span class="car-name">🚗 ${car.car_name}</span>
                                        <span class="car-income">${formatPrice(car.total_income)}$</span>
                                    </div>
                                    <div class="car-stat-details">
                                        <span class="detail">Аренд: ${car.rentals_count}</span>
                                        <span class="detail">Часов: ${car.total_hours}</span>
                                        <span class="detail">Среднее: ${formatPrice(car.total_income / car.rentals_count)}$/аренду</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
            
            const content = `
                <div class="stats-container">
                    <div class="time-filter-group">
                        <label for="rentalTimeFilter">Период:</label>
                        <select id="rentalTimeFilter" onchange="loadRentalStats()">
                            <option value="day" ${timeFilter === 'day' ? 'selected' : ''}>За день</option>
                            <option value="week" ${timeFilter === 'week' ? 'selected' : ''}>За неделю</option>
                            <option value="all" ${timeFilter === 'all' ? 'selected' : ''}>Всё время</option>
                        </select>
                    </div>
                    
                    <div class="stats-row">
                        <div class="stat-item">
                            <span class="stat-label">Всего авто:</span>
                            <span class="stat-value">${data.total_cars}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Аренд за период:</span>
                            <span class="stat-value">${data.total_rentals}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Доход за период:</span>
                            <span class="stat-value">${formatPrice(data.total_income)}$</span>
                        </div>
                        ${data.total_rentals > 0 ? `
                        <div class="stat-item">
                            <span class="stat-label">Среднее за аренду:</span>
                            <span class="stat-value">${formatPrice(data.total_income / data.total_rentals)}$</span>
                        </div>
                        ` : ''}
                    </div>
                    
                    ${carsTableHtml}
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
                    <div class="item-header">
                        <h4>${rental.car_name}</h4>
                        <button class="delete-btn" onclick="editRental(${rental.id}, ${rental.price_per_hour}, ${rental.hours}, '${rental.car_name}')" title="Редактировать">✎</button>
                    </div>
                    <p>⏰ ${rental.hours}ч × ${formatPrice(rental.price_per_hour)}$ = <strong>${formatPrice(rental.total_income)}$</strong></p>
                    <p class="small">🕐 ${rental.rental_start || 'Нет даты'}</p>
                    <p class="small">🕑 ${rental.rental_end || 'Нет даты'}</p>
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
