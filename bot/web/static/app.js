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
    
    // Закрываем все popup view'ы (статистика, история, скуп и т.д.)
    document.getElementById('statisticsView')?.classList.add('hidden');
    document.getElementById('historyView')?.classList.add('hidden');
    document.getElementById('purchasesView')?.classList.add('hidden');
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
    } else if (tabName === 'bp-farm') {
        loadBPTasks();
        loadBPStats();
    }
}

// Функция для закрытия всех popup view'ов
function closeAllPopups() {
    const popups = [
        'addItemForm',
        'addCarForm',
        'statisticsView',
        'historyView',
        'purchasesView',
        'inventoryView',
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
    
    const qtyInput = document.getElementById('itemQuantity').value;
    const quantity = qtyInput ? parseInt(qtyInput) : 1;
    
    const data = {
        name: document.getElementById('itemName').value,
        category: document.getElementById('itemCategory').value,
        price: parseFloat(document.getElementById('itemPrice').value),
        comment: document.getElementById('itemComment').value,
        quantity: quantity
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
    // Функция больше не используется - список товаров на главной удалён
    // Все товары теперь отображаются в подвкладках (Инвентарь, История продаж)
    return;
}

function sellItem(itemId) {
    const price = prompt('Введите цену продажи ($):');
    if (!price) return;
    
    submitSellItem(itemId, parseFloat(price));
}

async function submitSellItem(itemId, salePrice, quantity = 1) {
    try {
        const response = await fetch('/api/sell-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                item_id: itemId,
                price: salePrice,
                quantity: quantity
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            const profitText = result.profit >= 0 ? `+${formatPrice(result.profit)}` : formatPrice(result.profit);
            showNotification(`✅ ${result.message}\n💰 Прибыль: ${profitText}$`, 'success');
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
                    <div style="font-size: 24px; color: var(--accent-color);"><i class="fas fa-car"></i></div>
                    <h4 style="font-size: 12px; font-weight: 600; margin: 0; line-height: 1.2;">${car.name}</h4>
                    <p style="font-size: 11px; color: var(--text-secondary); margin: 0;"><i class="fas fa-coins"></i> ${formatPrice(car.cost)}$</p>
                    <button class="btn btn-small" onclick="openRentalModal(${car.id}, '${car.name}')" style="font-size: 11px; padding: 6px 10px; margin-top: auto;"><i class="fas fa-briefcase"></i> Сдать</button>
                </div>
            `).join('');
        } else {
            document.getElementById('carsList').innerHTML = `
                <div class="empty">
                    <p><i class="fas fa-car"></i> Автомобили будут отображаться здесь</p>
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

function openSaleModal(itemId, itemName, itemPrice, itemQty = 1) {
    if (itemQty > 1) {
        // Показываем модальное окно с выбором количества
        const modal = document.getElementById('saleModal');
        document.getElementById('saleItemId').value = itemId;
        document.getElementById('saleItemName').textContent = itemName;
        document.getElementById('saleAvgPrice').textContent = formatPrice(itemPrice);
        document.getElementById('saleMaxQty').textContent = itemQty;
        document.getElementById('saleQuantity').value = itemQty;
        document.getElementById('saleQuantity').max = itemQty;
        document.getElementById('salePrice').value = '';
        document.getElementById('salePrice').placeholder = `Цена за ${itemQty} шт.`;
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        document.getElementById('saleQuantity').focus();
    } else {
        // Обычный prompt для одиночного товара
        const price = prompt(`Введите цену продажи "${itemName}" (куплено за ${formatPrice(itemPrice)}$):`, itemPrice);
        if (!price) return;
        submitSellItem(itemId, parseFloat(price), 1);
    }
}

function updateSalePricePlaceholder() {
    const qty = document.getElementById('saleQuantity').value;
    document.getElementById('salePrice').placeholder = `Цена за ${qty} шт.`;
}

function closeSaleModal() {
    const modal = document.getElementById('saleModal');
    modal.classList.add('hidden');
    modal.style.display = 'none';
}

function submitSaleModal() {
    const itemId = document.getElementById('saleItemId').value;
    const quantity = parseInt(document.getElementById('saleQuantity').value);
    const price = parseFloat(document.getElementById('salePrice').value);
    
    if (!price || price <= 0) {
        showNotification('Введите цену продажи', 'error');
        return;
    }
    
    closeSaleModal();
    submitSellItem(itemId, price, quantity);
}

// Модальное окно для добавления количества
function openAddQtyModal(itemId, itemName, currentQty) {
    const modal = document.getElementById('addQtyModal');
    document.getElementById('addQtyItemId').value = itemId;
    document.getElementById('addQtyItemName').textContent = itemName;
    document.getElementById('addQtyCurrentQty').textContent = currentQty;
    document.getElementById('addQtyQuantity').value = 1;
    document.getElementById('addQtyPrice').value = '';
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    document.getElementById('addQtyQuantity').focus();
}

function closeAddQtyModal() {
    const modal = document.getElementById('addQtyModal');
    modal.classList.add('hidden');
    modal.style.display = 'none';
}

async function submitAddQty() {
    const itemId = document.getElementById('addQtyItemId').value;
    const quantity = parseInt(document.getElementById('addQtyQuantity').value);
    const price = parseFloat(document.getElementById('addQtyPrice').value);
    
    if (!quantity || quantity <= 0) {
        showNotification('Введите количество', 'error');
        return;
    }
    
    if (!price || price <= 0) {
        showNotification('Введите цену покупки', 'error');
        return;
    }
    
    closeAddQtyModal();
    
    try {
        const response = await fetch('/api/add-item-quantity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': userId
            },
            body: JSON.stringify({
                item_id: itemId,
                quantity: quantity,
                price: price
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`✅ ${result.message}\n📊 Средняя цена: ${formatPrice(result.avg_price)}$`, 'success');
            loadInventory();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
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
            // Фильтруем только непроданные товары (quantity > 0 и не sold)
            const unsoldItems = data.items.filter(item => !item.sold && (item.quantity || 1) > 0);
            
            if (unsoldItems.length > 0) {
                inventoryList.innerHTML = unsoldItems.map(item => {
                    const qty = item.quantity || 1;
                    const avgPrice = item.price;
                    const showAvg = qty > 1;
                    
                    return `
                    <div class="inventory-item">
                        <div class="inventory-item-main">
                            <div class="inventory-item-info">
                                <span class="inventory-item-name">${item.name}${qty > 1 ? ` <span class="qty-badge">×${qty}</span>` : ''}</span>
                                <span class="inventory-item-details">${item.category} • ${showAvg ? `~${formatPrice(avgPrice)}$/шт` : `${formatPrice(avgPrice)}$`}</span>
                            </div>
                            <div class="inventory-item-actions">
                                <button class="btn-add-qty" onclick="openAddQtyModal(${item.id}, '${item.name.replace(/'/g, "\\'")}', ${qty})" title="Добавить ещё"><i class="fas fa-plus"></i></button>
                                <button class="btn-sell-compact" onclick="openSaleModal(${item.id}, '${item.name.replace(/'/g, "\\'")}', ${avgPrice}, ${qty})">Продать</button>
                                <button class="btn-delete-compact" onclick="deleteItem(${item.id})"><i class="fas fa-xmark"></i></button>
                            </div>
                        </div>
                    </div>
                `}).join('');
            } else {
                inventoryList.innerHTML = '<p class="empty"><i class="fas fa-box"></i> Нет товаров в наличии</p>';
            }
        } else {
            inventoryList.innerHTML = `
                <div class="empty">
                    <p><i class="fas fa-box"></i> Товары будут отображаться здесь</p>
                    <p style="font-size: 12px; color: #bbb;">Добавьте первый товар кнопкой выше</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading inventory:', error);
        inventoryList.innerHTML = '<p class="error">Ошибка загрузки</p>';
    }
}

function searchInventory() {
    const query = document.getElementById('inventorySearch').value.toLowerCase();
    const items = document.getElementById('inventoryList').querySelectorAll('.inventory-item');
    
    items.forEach(item => {
        const name = item.querySelector('.inventory-item-name')?.textContent.toLowerCase() || '';
        item.style.display = name.includes(query) ? 'block' : 'none';
    });
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

// === СКУП (ИСТОРИЯ ЗАКУПОК) ===

function showPurchases() {
    closeAllPopups();
    const purchasesView = document.getElementById('purchasesView');
    purchasesView.classList.remove('hidden');
    loadPurchases();
    purchasesView.scrollIntoView({ behavior: 'smooth' });
}

function hidePurchases() {
    document.getElementById('purchasesView').classList.add('hidden');
}

async function loadPurchases() {
    const purchasesList = document.getElementById('purchasesList');
    purchasesList.innerHTML = '<p class="loading">Загрузка...</p>';
    
    try {
        const response = await fetch('/api/get-purchases', {
            headers: {'X-User-ID': userId}
        });
        
        const data = await response.json();
        
        if (data.success && data.purchases.length > 0) {
            let html = `
                <div class="stats-summary" style="background: var(--bg-tertiary); padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                    <p style="margin: 0; font-size: 14px;">
                        <i class="fas fa-shopping-cart"></i> Всего закупок: <strong>${data.purchases.length}</strong>
                        &nbsp;|&nbsp;
                        <i class="fas fa-coins"></i> На сумму: <strong>${formatPrice(data.total)}$</strong>
                    </p>
                </div>
            `;
            
            html += data.purchases.map(p => {
                const profit = p.sale_price ? (p.sale_price - p.price) : null;
                const profitClass = profit !== null ? (profit >= 0 ? 'positive' : 'negative') : '';
                
                return `
                <div class="item-card">
                    <div class="item-header">
                        <h4><i class="fas fa-box"></i> ${p.item_name}</h4>
                        ${p.can_delete ? `<button class="delete-btn" onclick="deletePurchase(${p.id})" title="Удалить"><i class="fas fa-xmark"></i></button>` : ''}
                    </div>
                    <p class="item-price"><i class="fas fa-coins"></i> Куплено: ${formatPrice(p.price)}$</p>
                    ${p.sale_price ? `
                        <p class="item-price" style="color: var(--success-color);"><i class="fas fa-receipt"></i> Продано: ${formatPrice(p.sale_price)}$</p>
                        <p class="profit ${profitClass}" style="font-weight: 600;"><i class="fas fa-chart-line"></i> Прибыль: ${profit >= 0 ? '+' : ''}${formatPrice(profit)}$</p>
                    ` : `<p class="item-price" style="color: var(--text-secondary);"><i class="fas fa-hourglass-half"></i> Не продано</p>`}
                    <p class="small" style="color: var(--text-secondary); margin-top: 4px;"><i class="fas fa-calendar"></i> ${p.created_at}</p>
                </div>
            `}).join('');
            
            purchasesList.innerHTML = html;
        } else {
            purchasesList.innerHTML = '<p class="empty"><i class="fas fa-shopping-cart"></i> Закупок пока нет. Добавьте товар в инвентарь — он автоматически появится здесь.</p>';
        }
    } catch (error) {
        console.error('Error loading purchases:', error);
        purchasesList.innerHTML = '<p class="error">Ошибка загрузки</p>';
    }
}

async function deletePurchase(purchaseId) {
    if (!confirm('Удалить эту запись из скупа?')) return;
    
    try {
        const response = await fetch(`/api/delete-purchase/${purchaseId}`, {
            method: 'DELETE',
            headers: {'X-User-ID': userId}
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Запись удалена', 'success');
            loadPurchases();
        } else {
            showNotification(data.error || 'Ошибка удаления', 'error');
        }
    } catch (error) {
        showNotification('Ошибка: ' + error.message, 'error');
    }
}

function searchPurchases() {
    const query = document.getElementById('purchaseSearch').value.toLowerCase();
    const items = document.getElementById('purchasesList').querySelectorAll('.item-card');
    
    items.forEach(item => {
        const name = item.querySelector('h4')?.textContent.toLowerCase() || '';
        item.style.display = name.includes(query) ? 'block' : 'none';
    });
}

function loadStatistics(timeFilter = 'all', dealFilter = 'all') {
    const statsContent = document.getElementById('statisticsContent');
    statsContent.innerHTML = '<p class="loading">Загрузка статистики...</p>';
    
    // Сохраняем текущие фильтры для графика
    currentSalesTimeFilter = timeFilter;
    
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
            
            // Рендерим график прибыли
            if (data.chart_data) {
                renderSalesChart(data.chart_data, timeFilter);
            }
            
            const content = `
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 15px; padding: 10px; background: var(--bg-secondary); border-radius: 6px;">
                    <i class="fas fa-chart-pie"></i> Фильтр: ${timeLabel}${dealLabel}
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
                ` : '<p class="empty"><i class="fas fa-chart-pie"></i> Нет данных для отображения</p>'}
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

// График прибыли перекупа
let salesChartInstance = null;
let currentSalesTimeFilter = 'all';

function renderSalesChart(chartData, timeFilter) {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;
    
    // Уничтожаем предыдущий график если есть
    if (salesChartInstance) {
        salesChartInstance.destroy();
    }
    
    const chartTitle = timeFilter === 'day' ? 'Прибыль по часам' : 
                       timeFilter === 'week' ? 'Прибыль по дням (неделя)' : 
                       'Прибыль за последние 30 дней';
    
    // Определяем цвета
    const computedStyle = getComputedStyle(document.body);
    const bgColor = computedStyle.getPropertyValue('--bg-primary').trim();
    const isDark = bgColor.includes('26') || bgColor.includes('30') || bgColor.includes('rgb(26') || 
                   document.body.style.backgroundColor?.includes('26') ||
                   window.Telegram?.WebApp?.colorScheme === 'dark';
    
    const textColor = isDark ? '#ffffff' : '#1a1a1a';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)';
    
    // Цвета столбцов: зелёный для прибыли, красный для убытка
    const backgroundColors = chartData.values.map(v => v >= 0 ? 'rgba(76, 175, 80, 0.7)' : 'rgba(244, 67, 54, 0.7)');
    const borderColors = chartData.values.map(v => v >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)');
    
    salesChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Прибыль ($)',
                data: chartData.values,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1,
                borderRadius: 4,
                minBarLength: 5 // Минимальная высота столбика для видимости
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index', // Наведение по всей вертикальной области
                intersect: false // Не нужно точно попадать в столбик
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: chartTitle,
                    color: textColor,
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.raw;
                            return (val >= 0 ? '+' : '') + formatPrice(val) + '$';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor,
                        callback: function(value) {
                            return (value >= 0 ? '+' : '') + formatPrice(value) + '$';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: textColor,
                        maxRotation: 45,
                        minRotation: 0,
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
    });
}

function loadHistory() {
    loadHistoryPage(1);
}

// Текущая страница истории
let currentHistoryPage = 1;
let totalHistoryPages = 1;

function loadHistoryPage(page) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '<p class="loading">Загрузка истории...</p>';
    
    currentHistoryPage = page;
    
    fetch(`/api/get-sales?page=${page}&per_page=15`, {
        headers: {
            'X-User-ID': userId
        }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success && data.sales.length > 0) {
            totalHistoryPages = data.total_pages;
            
            let html = data.sales.map(sale => `
                <div class="item-card">
                    <h4>${sale.item_name}</h4>
                    <p><i class="fas fa-receipt"></i> Продано за: <strong>${formatPrice(sale.sale_price)}$</strong></p>
                    <p><i class="fas fa-coins"></i> Куплено за: ${formatPrice(sale.purchase_price)}$</p>
                    <p class="profit ${sale.profit >= 0 ? 'positive' : 'negative'}">
                        <i class="fas fa-chart-line"></i> Прибыль: ${sale.profit >= 0 ? '+' : ''}${formatPrice(sale.profit)}$
                    </p>
                    <p class="small"><i class="fas fa-calendar"></i> ${new Date(sale.created_at).toLocaleString('ru-RU')}</p>
                </div>
            `).join('');
            
            // Добавляем пагинацию если страниц больше 1
            if (totalHistoryPages > 1) {
                html += renderHistoryPagination();
            }
            
            historyList.innerHTML = html;
        } else {
            historyList.innerHTML = '<p class="empty">История продаж пуста</p>';
        }
    })
    .catch(e => {
        console.error('Error loading history:', e);
        historyList.innerHTML = '<p class="error">Ошибка загрузки</p>';
    });
}

function renderHistoryPagination() {
    let paginationHtml = '<div class="pagination" style="display: flex; justify-content: center; align-items: center; gap: 8px; margin-top: 16px; flex-wrap: wrap;">';
    
    // Кнопка "Назад"
    if (currentHistoryPage > 1) {
        paginationHtml += `<button class="pagination-btn" onclick="loadHistoryPage(${currentHistoryPage - 1})" style="padding: 8px 12px; background: var(--bg-tertiary); border: none; border-radius: 8px; color: var(--text-primary); cursor: pointer;">
            <i class="fas fa-chevron-left"></i>
        </button>`;
    }
    
    // Номера страниц
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentHistoryPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalHistoryPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    if (startPage > 1) {
        paginationHtml += `<button class="pagination-btn" onclick="loadHistoryPage(1)" style="padding: 8px 12px; background: var(--bg-tertiary); border: none; border-radius: 8px; color: var(--text-primary); cursor: pointer;">1</button>`;
        if (startPage > 2) {
            paginationHtml += `<span style="color: var(--text-secondary);">...</span>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const isActive = i === currentHistoryPage;
        paginationHtml += `<button class="pagination-btn${isActive ? ' active' : ''}" onclick="loadHistoryPage(${i})" style="padding: 8px 12px; background: ${isActive ? 'var(--accent-color)' : 'var(--bg-tertiary)'}; border: none; border-radius: 8px; color: ${isActive ? 'white' : 'var(--text-primary)'}; cursor: pointer; font-weight: ${isActive ? '600' : '400'};">${i}</button>`;
    }
    
    if (endPage < totalHistoryPages) {
        if (endPage < totalHistoryPages - 1) {
            paginationHtml += `<span style="color: var(--text-secondary);">...</span>`;
        }
        paginationHtml += `<button class="pagination-btn" onclick="loadHistoryPage(${totalHistoryPages})" style="padding: 8px 12px; background: var(--bg-tertiary); border: none; border-radius: 8px; color: var(--text-primary); cursor: pointer;">${totalHistoryPages}</button>`;
    }
    
    // Кнопка "Вперед"
    if (currentHistoryPage < totalHistoryPages) {
        paginationHtml += `<button class="pagination-btn" onclick="loadHistoryPage(${currentHistoryPage + 1})" style="padding: 8px 12px; background: var(--bg-tertiary); border: none; border-radius: 8px; color: var(--text-primary); cursor: pointer;">
            <i class="fas fa-chevron-right"></i>
        </button>`;
    }
    
    paginationHtml += '</div>';
    paginationHtml += `<p style="text-align: center; font-size: 12px; color: var(--text-secondary); margin-top: 8px;">Страница ${currentHistoryPage} из ${totalHistoryPages}</p>`;
    
    return paginationHtml;
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
                    <div class="car-card" style="position: relative;">
                        <button class="delete-btn" onclick="deleteCar(${car.id})" title="Удалить" style="position: absolute; top: 8px; right: 8px;"><i class="fas fa-xmark"></i></button>
                        <div style="font-size: 20px; color: var(--accent-color);"><i class="fas fa-car"></i></div>
                        <h4 style="font-size: 12px; font-weight: 600; margin: 0; line-height: 1.2;">${car.name}</h4>
                        <p style="font-size: 10px; color: var(--text-secondary); margin: 0;"><i class="fas fa-coins"></i> ${formatPrice(car.cost)}$</p>
                        <div class="payback-bar" style="width: 100%; height: 3px; background: var(--bg-tertiary); border-radius: 2px; margin-top: 6px; overflow: hidden;">
                            <div class="payback-fill" style="height: 100%; width: ${Math.min(100, car.payback_percent)}%; background-color: ${paybackColor};"></div>
                        </div>
                        <p style="font-size: 9px; color: var(--text-secondary); margin: 4px 0 0 0;">🎯 ${car.payback_percent}%</p>
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
                        <h4><i class="fas fa-chart-pie"></i> Статистика по автомобилям:</h4>
                        <div class="cars-stats-table">
                            ${data.cars_stats.map(car => `
                                <div class="car-stat-item">
                                    <div class="car-stat-header">
                                        <span class="car-name"><i class="fas fa-car"></i> ${car.car_name}</span>
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
            
            // Отрисовываем график
            renderRentalChart(data.chart_data, timeFilter);
        } else {
            statsContent.innerHTML = '<p class="error">Ошибка загрузки</p>';
        }
    })
    .catch(e => {
        console.error('Error loading rental stats:', e);
        statsContent.innerHTML = '<p class="error">Ошибка загрузки</p>';
    });
}

// График доходов аренды
let rentalChartInstance = null;

function renderRentalChart(chartData, timeFilter) {
    const ctx = document.getElementById('rentalChart');
    if (!ctx) return;
    
    // Уничтожаем предыдущий график если есть
    if (rentalChartInstance) {
        rentalChartInstance.destroy();
    }
    
    const chartTitle = timeFilter === 'day' ? 'Доход по часам' : 
                       timeFilter === 'week' ? 'Доход по дням (неделя)' : 
                       'Доход за последние 30 дней';
    
    // Определяем цвета - берём из CSS переменных или используем контрастные цвета
    const computedStyle = getComputedStyle(document.body);
    const bgColor = computedStyle.getPropertyValue('--bg-primary').trim();
    
    // Если фон тёмный - используем светлый текст, иначе тёмный
    const isDark = bgColor.includes('26') || bgColor.includes('30') || bgColor.includes('rgb(26') || 
                   document.body.style.backgroundColor?.includes('26') ||
                   window.Telegram?.WebApp?.colorScheme === 'dark';
    
    const textColor = isDark ? '#ffffff' : '#1a1a1a';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)';
    
    rentalChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Доход ($)',
                data: chartData.values,
                backgroundColor: 'rgba(76, 175, 80, 0.7)',
                borderColor: 'rgba(76, 175, 80, 1)',
                borderWidth: 1,
                borderRadius: 4,
                minBarLength: 5 // Минимальная высота столбика для видимости
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index', // Наведение по всей вертикальной области
                intersect: false // Не нужно точно попадать в столбик
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: chartTitle,
                    color: textColor,
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return formatPrice(context.raw) + '$';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor,
                        callback: function(value) {
                            return formatPrice(value) + '$';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: textColor,
                        maxRotation: 45,
                        minRotation: 0,
                        font: {
                            size: 10
                        }
                    }
                }
            }
        }
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

// === BP FARM FUNCTIONS ===

function loadBPTasks() {
    const container = document.getElementById('bpTasksContainer');
    container.innerHTML = '<p class="loading">Загрузка...</p>';
    
    fetch('/api/get-bp-tasks', {
        headers: {'X-User-ID': userId}
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            // Обновляем чекбокс VIP
            document.getElementById('platinumVipToggle').checked = data.has_platinum_vip;
            
            const categories = ['Легкие', 'Средние', 'Тяжелые'];
            let html = '';
            
            categories.forEach(category => {
                if (data.tasks[category]) {
                    html += `
                        <div class="bp-category">
                            <h3 onclick="toggleCategory('${category}')" style="cursor: pointer;">
                                <span class="arrow collapsed">▶</span> ${category} (${data.tasks[category].length})
                            </h3>
                            <div class="bp-tasks collapsed" id="category-${category}">
                    `;
                    
                    data.tasks[category].forEach(task => {
                        const bpValue = data.has_platinum_vip ? task.bp_with_vip : task.bp_without_vip;
                        const checked = task.is_completed ? 'checked' : '';
                        
                        html += `
                            <div class="bp-task-item">
                                <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; flex: 1;">
                                    <input type="checkbox" ${checked} onchange="toggleBPTask(${task.id}, this.checked)">
                                    <span>${task.name}</span>
                                </label>
                                <div class="bp-value">
                                    ${task.bp_without_vip}/${task.bp_with_vip} BP
                                </div>
                            </div>
                        `;
                    });
                    
                    html += `
                            </div>
                        </div>
                    `;
                }
            });
            
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="error">Ошибка загрузки</p>';
        }
    })
    .catch(err => {
        container.innerHTML = '<p class="error">Ошибка загрузки</p>';
    });
}

function toggleCategory(category) {
    const elem = document.getElementById(`category-${category}`);
    const arrow = elem?.parentElement?.querySelector('.arrow');
    
    if (elem) {
        elem.classList.toggle('collapsed');
        if (arrow) {
            arrow.classList.toggle('collapsed');
        }
    }
}

function toggleBPTask(taskId, isCompleted) {
    fetch(`/api/toggle-bp-task/${taskId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-User-ID': userId
        },
        body: JSON.stringify({ is_completed: isCompleted })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            loadBPStats();
        }
    })
    .catch(err => console.error('Error:', err));
}

function loadBPStats() {
    fetch('/api/get-bp-stats', {
        headers: {'X-User-ID': userId}
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            document.getElementById('bpToday').textContent = data.bp_today;
            document.getElementById('bpWeek').textContent = data.bp_week;
            document.getElementById('bpTotal').textContent = data.bp_total;
        }
    })
    .catch(err => console.error('Error:', err));
}

function togglePlatinumVip() {
    const hasVip = document.getElementById('platinumVipToggle').checked;
    
    fetch('/api/toggle-platinum-vip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-User-ID': userId
        },
        body: JSON.stringify({ has_platinum_vip: hasVip })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showNotification(hasVip ? '💎 Платинум VIP включен' : '💎 Платинум VIP выключен', 'success');
            loadBPTasks();
            loadBPStats();
        }
    })
    .catch(err => console.error('Error:', err));
}


// ========== ТАЙМЕРЫ ==========

// Объект для хранения активных таймеров
let activeTimers = {};

// Функция запуска таймера
function startTimer(timerName, duration) {
    // Если таймер уже запущен, не запускаем еще один
    if (activeTimers[timerName]) {
        showNotification(`⏱️ Таймер "${timerName}" уже запущен!`, 'warning');
        return;
    }
    
    const timerData = {
        name: timerName,
        duration: duration,
        remaining: duration,
        startTime: Date.now(),
        endTime: Date.now() + (duration * 1000),
        interval: null,
        paused: false
    };
    
    activeTimers[timerName] = timerData;
    
    // Показываем контейнер активных таймеров
    document.getElementById('activeTimersContainer').classList.remove('hidden');
    
    // Отмечаем кнопку как активную
    document.querySelectorAll('.timer-btn').forEach(btn => {
        if (btn.dataset.timerName === timerName) {
            btn.classList.add('active');
        }
    });
    
    // Показываем уведомление
    showNotification(`⏱️ Запущен таймер "${timerName}"`, 'success');
    
    // Отрисовываем таймер
    renderActiveTimer(timerName);
    
    // Начинаем обратный отсчет
    startTimerCountdown(timerName);
}

// Функция для отрисовки активного таймера
function renderActiveTimer(timerName) {
    const timerData = activeTimers[timerName];
    const listContainer = document.getElementById('activeTimersList');
    
    // Проверяем, есть ли уже элемент для этого таймера
    let timerElement = document.getElementById(`timer-${timerName}`);
    
    if (!timerElement) {
        timerElement = document.createElement('div');
        timerElement.id = `timer-${timerName}`;
        timerElement.className = 'active-timer-item';
        timerElement.innerHTML = `
            <div class="active-timer-info">
                <div class="active-timer-name">${timerName}</div>
                <div class="active-timer-display" id="timer-display-${timerName}">00:00:00</div>
                <div class="timer-progress-bar">
                    <div class="timer-progress-fill" id="timer-progress-${timerName}" style="width: 100%;"></div>
                </div>
            </div>
            <div class="active-timer-controls">
                <button class="timer-control-btn" id="pause-btn-${timerName}" onclick="togglePauseTimer('${timerName}')">
                    <i class="fas fa-pause"></i> Пауза
                </button>
                <button class="timer-stop-btn" onclick="stopTimer('${timerName}')">
                    <i class="fas fa-times-circle"></i> Стоп
                </button>
            </div>
        `;
        listContainer.appendChild(timerElement);
    }
}

// Функция для обратного отсчета
function startTimerCountdown(timerName) {
    const timerData = activeTimers[timerName];
    
    // Если интервал уже существует, очищаем его
    if (timerData.interval) {
        clearInterval(timerData.interval);
    }
    
    // Обновляем дисплей каждые 100ms для плавности
    timerData.interval = setInterval(() => {
        const now = Date.now();
        const remaining = timerData.endTime - now;
        
        if (remaining <= 0) {
            // Таймер завершён
            clearInterval(timerData.interval);
            completeTimer(timerName);
        } else {
            // Обновляем оставшееся время
            timerData.remaining = remaining;
            updateTimerDisplay(timerName);
        }
    }, 100);
}

// Функция обновления отображения таймера
function updateTimerDisplay(timerName) {
    const timerData = activeTimers[timerName];
    const remaining = timerData.remaining;
    
    // Конвертируем в часы, минуты, секунды
    const totalSeconds = Math.ceil(remaining / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    
    // Форматируем строку времени
    const timeString = [
        String(hours).padStart(2, '0'),
        String(minutes).padStart(2, '0'),
        String(seconds).padStart(2, '0')
    ].join(':');
    
    // Обновляем дисплей
    const display = document.getElementById(`timer-display-${timerName}`);
    if (display) {
        display.textContent = timeString;
    }
    
    // Обновляем прогресс бар
    const progressBar = document.getElementById(`timer-progress-${timerName}`);
    if (progressBar) {
        const progress = (remaining / (timerData.duration * 1000)) * 100;
        progressBar.style.width = Math.max(0, progress) + '%';
    }
}

// Функция завершения таймера
function completeTimer(timerName) {
    const timerData = activeTimers[timerName];
    
    // Звуковое уведомление
    playTimerSound();
    
    // Показываем уведомление
    showNotification(`✅ Таймер "${timerName}" завершён!`, 'success');
    
    // Отправляем сообщение в телеграм
    sendTimerNotificationToTelegram(timerName);
    
    // Удаляем из активных
    delete activeTimers[timerName];
    
    // Удаляем элемент из DOM
    const timerElement = document.getElementById(`timer-${timerName}`);
    if (timerElement) {
        timerElement.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => timerElement.remove(), 300);
    }
    
    // Убираем активный статус кнопки
    document.querySelectorAll('.timer-btn').forEach(btn => {
        if (btn.dataset.timerName === timerName) {
            btn.classList.remove('active');
        }
    });
    
    // Если нет активных таймеров, скрываем контейнер
    if (Object.keys(activeTimers).length === 0) {
        document.getElementById('activeTimersContainer').classList.add('hidden');
    }
}

// Функция остановки таймера
function stopTimer(timerName) {
    if (activeTimers[timerName]) {
        clearInterval(activeTimers[timerName].interval);
        delete activeTimers[timerName];
        
        // Удаляем элемент из DOM
        const timerElement = document.getElementById(`timer-${timerName}`);
        if (timerElement) {
            timerElement.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => timerElement.remove(), 300);
        }
        
        // Убираем активный статус кнопки
        document.querySelectorAll('.timer-btn').forEach(btn => {
            if (btn.dataset.timerName === timerName) {
                btn.classList.remove('active');
            }
        });
        
        showNotification(`⏹️ Таймер "${timerName}" остановлен`, 'info');
        
        // Если нет активных таймеров, скрываем контейнер
        if (Object.keys(activeTimers).length === 0) {
            document.getElementById('activeTimersContainer').classList.add('hidden');
        }
    }
}

// Функция для воспроизведения звука
function playTimerSound() {
    // Проигрываем пользовательский звук из файла
    try {
        const audio = new Audio('/static/sound.mp3');
        audio.volume = 0.8; // Громкость 80%
        audio.play().catch(err => {
            console.warn('Could not play sound:', err);
            // Если не удалось воспроизвести файл, используем встроенный звук
            playFallbackSound();
        });
    } catch(e) {
        console.warn('Audio playback not available:', e);
        playFallbackSound();
    }
}

// Резервный встроенный звук (если файл не найден)
function playFallbackSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const now = audioContext.currentTime;
        
        // Создаем два бипа
        const osc1 = audioContext.createOscillator();
        const gain1 = audioContext.createGain();
        osc1.connect(gain1);
        gain1.connect(audioContext.destination);
        
        const osc2 = audioContext.createOscillator();
        const gain2 = audioContext.createGain();
        osc2.connect(gain2);
        gain2.connect(audioContext.destination);
        
        // Первый биз
        osc1.frequency.setValueAtTime(800, now);
        osc1.frequency.setValueAtTime(1000, now + 0.1);
        gain1.gain.setValueAtTime(0.3, now);
        gain1.gain.setValueAtTime(0, now + 0.2);
        osc1.start(now);
        osc1.stop(now + 0.2);
        
        // Второй биз (на 300ms позже)
        osc2.frequency.setValueAtTime(1000, now + 0.3);
        osc2.frequency.setValueAtTime(1200, now + 0.4);
        gain2.gain.setValueAtTime(0.3, now + 0.3);
        gain2.gain.setValueAtTime(0, now + 0.5);
        osc2.start(now + 0.3);
        osc2.stop(now + 0.5);
    } catch(e) {
        console.warn('Fallback sound not available:', e);
    }
}

// Функция отправки уведомления в телеграм
function sendTimerNotificationToTelegram(timerName) {
    // Отправляем запрос к серверу для отправки сообщения в телеграм
    fetch('/api/send-timer-notification', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-User-ID': userId
        },
        body: JSON.stringify({
            timer_name: timerName
        })
    })
    .catch(err => console.error('Error sending timer notification:', err));
}

// Функция показа формы создания собственного таймера
function showCustomTimerForm() {
    document.getElementById('customTimerForm').classList.remove('hidden');
}

// Функция скрытия формы создания собственного таймера
function hideCustomTimerForm() {
    document.getElementById('customTimerForm').classList.add('hidden');
    // Очищаем поля
    document.getElementById('customTimerName').value = '';
    document.getElementById('customTimerHours').value = '0';
    document.getElementById('customTimerMinutes').value = '5';
    document.getElementById('customTimerSeconds').value = '0';
}

// Функция запуска собственного таймера
function startCustomTimer() {
    const name = document.getElementById('customTimerName').value.trim();
    const hours = parseInt(document.getElementById('customTimerHours').value) || 0;
    const minutes = parseInt(document.getElementById('customTimerMinutes').value) || 0;
    const seconds = parseInt(document.getElementById('customTimerSeconds').value) || 0;
    
    // Проверяем валидность
    if (!name) {
        showNotification('❌ Введите название таймера', 'danger');
        return;
    }
    
    if (hours === 0 && minutes === 0 && seconds === 0) {
        showNotification('❌ Установите время больше 0', 'danger');
        return;
    }
    
    if (activeTimers[name]) {
        showNotification(`⏱️ Таймер "${name}" уже запущен!`, 'warning');
        return;
    }
    
    // Конвертируем в секунды
    const totalSeconds = hours * 3600 + minutes * 60 + seconds;
    
    // Скрываем форму
    hideCustomTimerForm();
    
    // Запускаем таймер
    startTimer(name, totalSeconds);
}

// Функция паузы/продолжения таймера
function togglePauseTimer(timerName) {
    const timerData = activeTimers[timerName];
    if (!timerData) return;
    
    const pauseBtn = document.getElementById(`pause-btn-${timerName}`);
    
    if (timerData.paused) {
        // Продолжаем таймер
        timerData.paused = false;
        timerData.endTime = Date.now() + timerData.remaining;
        pauseBtn.innerHTML = '<i class="fas fa-pause"></i> Пауза';
        showNotification(`▶️ Таймер "${timerName}" продолжен`, 'info');
        startTimerCountdown(timerName);
    } else {
        // Ставим на паузу
        timerData.paused = true;
        clearInterval(timerData.interval);
        pauseBtn.innerHTML = '<i class="fas fa-play"></i> Продолжить';
        showNotification(`⏸️ Таймер "${timerName}" на паузе`, 'warning');
    }
}

// Добавляем анимацию для выезда элемента
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(-100%);
        }
    }
`;
document.head.appendChild(style);

// ========== ГАЙДЫ ==========

function toggleGuideSection(btn) {
    const content = btn.parentElement.querySelector('.guide-section-content');
    
    // Если закрыта, открываем
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        btn.classList.add('expanded');
    } else {
        content.classList.add('hidden');
        btn.classList.remove('expanded');
    }
}

function toggleAnswer(btn) {
    const answerContainer = btn.parentElement.querySelector('.answer-container');
    
    // Если закрыта, открываем
    if (answerContainer.classList.contains('hidden')) {
        answerContainer.classList.remove('hidden');
        btn.classList.add('expanded');
    } else {
        answerContainer.classList.add('hidden');
        btn.classList.remove('expanded');
    }
}

// Обработчик переключения подвкладок гайдов (если будут в будущем)
document.addEventListener('DOMContentLoaded', function() {
    const guideBtns = document.querySelectorAll('.guide-btn');
    guideBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const guideId = this.getAttribute('data-guide');
            
            // Снимаем active со всех кнопок и скрываем все контенты
            document.querySelectorAll('.guide-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.guide-content').forEach(c => c.classList.remove('active'));
            
            // Добавляем active к текущей кнопке и показываем контент
            this.classList.add('active');
            const guideContent = document.getElementById(guideId);
            if (guideContent) {
                guideContent.classList.add('active');
            }
        });
    });
});

