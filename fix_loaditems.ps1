$content = Get-Content -Path "bot/web/static/app.js" -Raw

# Используем простой sed-like замену через Replace
$newFunc = @'
async function loadItems() {
    // Вкладка "Ваши товары" больше не используется
    // История продаж отображается в отдельной вкладке "История продаж"
    // Все товары в наличии показываются в "Инвентарь"
    
    const itemsList = document.getElementById('itemsList');
    if (itemsList) {
        itemsList.innerHTML = `
            <div class="empty">
                <p>📦 Используйте "Инвентарь" для товаров в наличии</p>
                <p style="font-size: 12px; color: #bbb;">И "История продаж" для проданных товаров</p>
            </div>
        `;
    }
}
'@

# Находим начало функции
$pattern = "async function loadItems\(\) \{.*?\n\}"
$content = $content -replace $pattern, $newFunc, 1

Set-Content -Path "bot/web/static/app.js" -Value $content -Encoding UTF8
Write-Host "✅ Файл обновлен"
